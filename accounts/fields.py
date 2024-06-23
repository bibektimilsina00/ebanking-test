from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django.db.models import Field
from django.db.models.lookups import Exact
from cryptography.fernet import Fernet

# Generate a key for encryption and decryption
# This key should be securely stored and must be the same for encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

class EncryptedEmailField(models.BinaryField):
    def get_internal_type(self):
        return "BinaryField"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return cipher_suite.decrypt(value).decode()
        except Exception as e:
            return None  # Or handle error appropriately

    def to_python(self, value):
        if isinstance(value, bytes):
            return cipher_suite.decrypt(value).decode()
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return cipher_suite.encrypt(value.encode())

class EncryptedExact(Exact):
    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s = %s' % (lhs, rhs), params

Field.register_lookup(EncryptedExact)