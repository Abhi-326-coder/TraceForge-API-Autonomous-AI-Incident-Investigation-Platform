export type LoginValidationErrors = {
  email?: string;
  password?: string;
};

export function validateLogin(email: string, password: string): LoginValidationErrors {
  const errors: LoginValidationErrors = {};

  if (!email.trim()) {
    errors.email = "Enter your email address.";
  } else if (!/^\S+@\S+\.\S+$/.test(email)) {
    errors.email = "Enter a valid email address.";
  }

  if (!password) {
    errors.password = "Enter your password.";
  }

  return errors;
}
