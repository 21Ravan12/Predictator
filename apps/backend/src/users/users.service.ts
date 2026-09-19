import {
  Injectable,
  Logger,
  ConflictException,
  BadRequestException,
} from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { CreateUserDto } from './dto/create-user.dto';
import * as bcrypt from 'bcrypt';

export interface User {
  id: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  roles: string[];
  createdAt: Date;
  updatedAt: Date;
}

@Injectable()
export class UsersService {
  private readonly logger = new Logger(UsersService.name);

  constructor(private databaseService: DatabaseService) {}

  async create(createUserDto: CreateUserDto): Promise<Omit<User, 'password'>> {
    return this.createUser(createUserDto);
  }

  private withoutPassword(user: User): Omit<User, 'password'> {
    const userWithoutPassword = { ...user } as Partial<User>;
    delete userWithoutPassword.password;
    return userWithoutPassword as Omit<User, 'password'>;
  }

  async createUser(
    createUserDto: CreateUserDto,
  ): Promise<Omit<User, 'password'>> {
    this.logger.log(`📝 Creating user: ${createUserDto.email}`);

    if (!createUserDto.email) {
      throw new BadRequestException('Email is required');
    }

    const existingUser = await this.findByEmail(createUserDto.email);
    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }

    const user = await this.databaseService.createUser({
      ...createUserDto,
      roles: createUserDto.roles || ['user'],
    });

    this.logger.log(`✅ User created: ${createUserDto.email}`);
    return this.withoutPassword(user);
  }

  async findAll(): Promise<Omit<User, 'password'>[]> {
    this.logger.log('📋 Finding all users');
    const users = (await this.databaseService.findAllUsers()) as User[];
    return users.map((user) => this.withoutPassword(user));
  }

  async findById(id: string): Promise<Omit<User, 'password'> | null> {
    this.logger.log(`🔍 Finding user by ID: ${id}`);
    const user = await this.databaseService.findUserById(id);
    if (!user) return null;
    return this.withoutPassword(user);
  }

  async findByEmail(email: string): Promise<User | null> {
    this.logger.log(`🔍 Finding user by email: ${email}`);
    return await this.databaseService.findUserByEmail(email);
  }

  async update(
    id: string,
    updateData: Partial<CreateUserDto>,
  ): Promise<Omit<User, 'password'> | null> {
    this.logger.log(`🔄 Updating user: ${id}`);

    if (updateData.password) {
      updateData.password = await bcrypt.hash(updateData.password, 10);
    }

    const user = (await this.databaseService.updateUser(
      id,
      updateData,
    )) as User | null;
    if (!user) return null;

    return this.withoutPassword(user);
  }

  delete(id: string): Promise<boolean> {
    this.logger.log(`🗑️ Deleting user: ${id}`);
    return this.databaseService.deleteUser(id);
  }
}
