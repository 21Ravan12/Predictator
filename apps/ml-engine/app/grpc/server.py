# app/grpc/server.py
"""gRPC Server for Predictator ML Engine"""

import grpc
from concurrent import futures
import logging
from datetime import datetime, timedelta

# Import generated gRPC code
from .generated import predictor_pb2
from .generated import predictor_pb2_grpc

# Import your engine
from ..core.predictor import PredictatorEngine
from ..models import DatabaseManager

logger = logging.getLogger(__name__)


class PredictorServicer(predictor_pb2_grpc.PredictorServiceServicer):
    """gRPC server implementation"""

    def __init__(self):
        self.predictator = PredictatorEngine()
        self.db = DatabaseManager()
        
        # Load existing model if available
        try:
            self.predictator._load_model()
            logger.info("✅ Model loaded for gRPC server")
        except Exception as e:
            logger.warning(f"⚠️ No model loaded: {e}")

    def GetPrediction(self, request, context):
        """Generate predictions for a product"""
        try:
            logger.info(f"📊 gRPC: Prediction request for {request.product_id}")
            
            # Load history from database
            history = self.db.load_sales_history(
                request.product_id,
                days_back=180,
            )
            
            if len(history) < 30:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(
                    f"Need 30+ days of history. Only have {len(history)}"
                )
                return predictor_pb2.PredictionResponse(success=False)

            # Generate predictions
            predictions, conf_intervals, _ = self.predictator.predict(
                days_ahead=request.days_ahead,
                last_sales=history,
            )

            # Build response
            response = predictor_pb2.PredictionResponse(
                success=True,
                product_id=request.product_id,
            )

            # Add predictions
            future_dates = [
                (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
                for i in range(request.days_ahead)
            ]

            final_predictions = []
            floor_violations = 0

            for i, (pred, conf) in enumerate(zip(predictions, conf_intervals)):
                # Apply floor limit
                final, alert = self.predictator.enforce_floor_limit(
                    pred, request.floor_limit
                )
                final_predictions.append(final)

                # Add to response
                pred_item = response.predictions.add()
                pred_item.date = future_dates[i]
                pred_item.predicted_sales = float(final)
                pred_item.confidence_lower = float(conf[0])
                pred_item.confidence_upper = float(conf[1])
                pred_item.alert = alert or ""

                # Track dictator actions
                if alert:
                    floor_violations += 1
                    action = response.dictator_actions.add()
                    action.day = i + 1
                    action.message = alert

            # Summary
            response.summary.total_predicted = float(sum(final_predictions))
            response.summary.average_daily = float(
                sum(final_predictions) / len(final_predictions)
            )
            response.summary.peak_day = float(max(final_predictions))
            response.summary.floor_violations = floor_violations

            logger.info(
                f"✅ gRPC: Generated {len(predictions)} predictions "
                f"({floor_violations} floor violations)"
            )
            return response

        except Exception as e:
            logger.error(f"❌ gRPC prediction error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return predictor_pb2.PredictionResponse(success=False)

    def TrainModel(self, request, context):
        """Train the model"""
        try:
            logger.info(f"🧠 gRPC: Training request (csv={request.csv_path})")
            
            # Load data
            if request.csv_path:
                import pandas as pd
                df = pd.read_csv(request.csv_path, parse_dates=['date'])
            else:
                df = self.predictator.generate_sample_data()

            # Train
            metrics = self.predictator.train(df)
            self.predictator.save_model()

            # Save to database
            if len(df) > 0:
                self.db.save_sales_history(df)

            # Build response
            response = predictor_pb2.TrainResponse(
                success=True,
                message="Model trained successfully!",
                samples_used=len(df),
            )
            response.metrics.r2 = float(metrics.get('r2', 0))
            response.metrics.mae = float(metrics.get('mae', 0))
            response.metrics.rmse = float(metrics.get('rmse', 0))
            response.metrics.n_features = int(metrics.get('n_features', 0))

            logger.info(f"✅ gRPC: Training complete! R²: {metrics.get('r2', 0):.3f}")
            return response

        except Exception as e:
            logger.error(f"❌ gRPC training error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return predictor_pb2.TrainResponse(success=False)

    def GetTrainingStatus(self, request, context):
        """Get training status"""
        try:
            response = predictor_pb2.TrainingStatusResponse(
                is_trained=self.predictator.is_trained,
            )

            if self.predictator.last_training_date:
                response.last_training_date = (
                    self.predictator.last_training_date.isoformat()
                )

            metrics = self.predictator.training_metrics or {}
            response.metrics.r2 = float(metrics.get('r2', 0))
            response.metrics.mae = float(metrics.get('mae', 0))
            response.metrics.rmse = float(metrics.get('rmse', 0))
            response.metrics.n_features = int(metrics.get('n_features', 0))

            return response

        except Exception as e:
            logger.error(f"❌ gRPC status error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return predictor_pb2.TrainingStatusResponse()


def serve_grpc(port: int = 50051):
    """Start the gRPC server (blocking)"""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ],
    )
    
    predictor_pb2_grpc.add_PredictorServiceServicer_to_server(
        PredictorServicer(), server
    )
    
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"🚀 gRPC server running on port {port}")
    
    return server


def start_grpc_server_in_thread(port: int = 50051):
    """Start gRPC server in a background thread"""
    import threading
    server = serve_grpc(port)
    thread = threading.Thread(target=server.wait_for_termination, daemon=True)
    thread.start()
    return server