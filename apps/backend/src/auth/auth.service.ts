import {
  Injectable,
  UnauthorizedException,
  ConflictException,
  Logger,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { User, UsersService } from '../users/users.service';
import { LoginDto } from './dto/login.dto';
import { RegisterDto } from './dto/register.dto';

type SafeUser = Omit<User, 'password'>;

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private usersService: UsersService,
    private jwtService: JwtService,
  ) {}

  async validateUser(email: string, password: string): Promise<SafeUser> {
    this.logger.log(`🔍 Validating user: ${email}`);
    const user = await this.usersService.findByEmail(email);

    if (!user) {
      this.logger.warn(`❌ User not found: ${email}`);
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      this.logger.warn(`❌ Invalid password for: ${email}`);
      throw new UnauthorizedException('Invalid credentials');
    }

    this.logger.log(`✅ User validated: ${email}`);
    return {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      roles: user.roles,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    };
  }

  async login(loginDto: LoginDto) {
    this.logger.log(`🔐 Login attempt: ${loginDto.email}`);
    const user = await this.validateUser(loginDto.email, loginDto.password);

    const payload = {
      sub: user.id,
      email: user.email,
      roles: user.roles || ['user'],
    };

    this.logger.log(`✅ Login successful: ${loginDto.email}`);
    return {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        roles: user.roles || ['user'],
      },
    };
  }

  async register(registerDto: RegisterDto) {
    this.logger.log(`📝 Register attempt: ${registerDto.email}`);

    const existingUser = await this.usersService.findByEmail(registerDto.email);
    if (existingUser) {
      this.logger.warn(`❌ User already exists: ${registerDto.email}`);
      throw new ConflictException('User with this email already exists');
    }

    const hashedPassword = await bcrypt.hash(registerDto.password, 10);

    const user = await this.usersService.create({
      ...registerDto,
      password: hashedPassword,
    });

    this.logger.log(`✅ User registered: ${registerDto.email}`);
    return user;
  }

  async getProfile(userId: string) {
    this.logger.log(`👤 Getting profile for: ${userId}`);
    const user = await this.usersService.findById(userId);
    if (!user) {
      throw new UnauthorizedException('User not found');
    }
    return user;
  }

  async refreshToken(userId: string) {
    this.logger.log(`🔄 Refreshing token for: ${userId}`);
    const user = await this.usersService.findById(userId);
    if (!user) {
      throw new UnauthorizedException('User not found');
    }

    const payload = {
      sub: user.id,
      email: user.email,
      roles: user.roles || ['user'],
    };

    return {
      access_token: this.jwtService.sign(payload),
    };
  }

  logout(userId: string) {
    this.logger.log(`🚪 User logged out: ${userId}`);
    return { message: 'Logged out successfully' };
  }
}
