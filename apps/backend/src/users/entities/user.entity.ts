export class UserEntity {
  id: string | undefined;
  email: string | undefined;
  password: string | undefined;
  firstName: string | undefined;
  lastName: string | undefined;
  roles: string[] | undefined;
  createdAt: Date | undefined;
  updatedAt: Date | undefined;

  constructor(partial: Partial<UserEntity>) {
    Object.assign(this, partial);
  }

  toJSON() {
    const { ...result } = this;
    return result;
  }
}
