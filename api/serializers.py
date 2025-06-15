from rest_framework import serializers
from django.contrib.auth import authenticate # Функция authenticate из Django
from rest_framework_simplejwt.tokens import RefreshToken # Для генерации токенов
from dj_rest_auth.serializers import LoginSerializer
from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_user_model
from api.models import Vacancy, VacancyResponse


User = get_user_model()

class CustomLoginSerializer(LoginSerializer):
    # Мы явно убираем поле 'username' из ожидаемых входных данных
    # Если вы хотите, чтобы это поле *не* отображалось в схеме или в форме Swagger/Redoc,
    # и точно не участвовало во входе, то можно его просто не определять,
    # а в validate() использовать только email.
    # Но для полной ясности и подавления возможных предупреждений, можно сделать так:
    username = serializers.CharField(
        required=False, # Не требуется для пользователя
        allow_blank=True,
        write_only=True, # Только для записи, не отображается в ответе
        help_text="Оставьте пустым, мы используем Email." # Помогает в документации
    )

    # Делаем email ОБЯЗАТЕЛЬНЫМ полем для входа
    email = serializers.EmailField(required=True, allow_blank=False)

    # *** ПЕРЕОПРЕДЕЛЯЕМ МЕТОД VALIDATE ДЛЯ ПРЯМОЙ АУТЕНТИФИКАЦИИ ПО EMAIL ***
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Если email или пароль отсутствуют, Django-сериализатор уже выдаст ошибку required=True
        # Но для надежности можно добавить проверку:
        if not email or not password:
            raise serializers.ValidationError("Необходимо указать email и пароль.")

        # !!! ПРЯМОЙ ВЫЗОВ БЭКЕНДА АУТЕНТИФИКАЦИИ ALLAUTH С ИСПОЛЬЗОВАНИЕМ EMAIL !!!
        user = AuthenticationBackend().authenticate(
            request=self.context.get('request'), # Передаем request
            email=email,
            password=password
        )

        if not user:
            # Если аутентификация не удалась, выдаем общее сообщение
            raise serializers.ValidationError("Невозможно войти в систему с указанными учётными данными.")

        # Если пользователь найден, но неактивен, выдаем ошибку
        if not user.is_active:
            raise serializers.ValidationError("Учетная запись не активна.")

        # Если верификация email обязательна (хотя у вас 'none'), можно добавить проверку:
        # if (allauth_account_settings.EMAIL_VERIFICATION == allauth_account_settings.EmailVerificationMethod.MANDATORY and
        #     not allauth_account_settings.ADAPTER.get_email_confirmation_for_user(user)):
        #     raise serializers.ValidationError("Email не подтвержден. Пожалуйста, проверьте свой почтовый ящик.")

        # Добавляем найденного пользователя в validated_data
        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    user_r = serializers.BooleanField(
        required=False,  # Сделать необязательным, если пользователь не отметит
        default=False,  # По умолчанию считаем, что пользователь не рекрутер
        help_text="Отметьте, если вы хотите публиковать вакансии."
    )
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def save(self, request):
        user = super().save(request)  # Сначала вызываем родительский save(), чтобы создать пользователя

        # Теперь устанавливаем значение user_r на основе поля is_recruiter
        # Если is_recruiter не было предоставлено или было False, user_r будет False (по умолчанию)
        user.user_r = self.validated_data.get('user_r', False)
        user.save()

        return user

    class Meta:
        model = get_user_model()
        fields = ('username', 'user_r', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, data):
        # Проверка совпадения паролей
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        # Проверка уникальности email
        if get_user_model().objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует."})
        return data

    @staticmethod
    def validate_email(value):
        # Проверка уникальности email при регистрации
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        # Удаляем password_confirm, так как он не нужен для создания объекта User
        validated_data.pop('password_confirm')
        username = validated_data['email'] # Используем email как username
        if get_user_model().objects.filter(username=username).exists():
             # Если username (email) уже занят, можно добавить суффикс или попросить пользователя ввести username
            username = f"{validated_data['email'].split('@')[0]}_{get_user_model().objects.count() + 1}" # Очень простой способ избежать дубликатов

        user = get_user_model().objects.create_user(
            username=username, # Заменили на сгенерированный username
            email=validated_data['email'],
            user_r=validated_data['user_r'],
            password=validated_data['password'],
        )
        return user


class CustomAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    # Эти поля не будут приниматься на вход, но будут возвращаться в ответе
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Используем authenticate для проверки учетных данных
            # Если вы настроили SIMPLE_JWT['USERNAME_FIELD'] = 'email',
            # то authenticate будет искать пользователя по email.
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                # Если пользователь не найден или пароль неверный
                raise serializers.ValidationError('Неверные учетные данные.', code='authentication')
        else:
            raise serializers.ValidationError('Необходимо указать email и пароль.', code='no_credentials')

        # Если аутентификация прошла успешно, сохраняем пользователя в контексте
        # Это позволяет получить доступ к пользователю в методе .save() или .create()
        self.user = user

        # Генерируем токены
        refresh = RefreshToken.for_user(user) # Создаем refresh токен
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token) # Получаем access токен из refresh токена

        return data

    def create(self, validated_data):
        # В случае авторизации, мы не "создаем" новый объект User,
        # а только возвращаем токены и информацию о пользователе.
        # Метод validate уже обработал аутентификацию и сгенерировал токены.
        # Мы просто возвращаем данные, которые уже были добавлены в `validated_data`
        # в методе `validate`.
        return {
            'email': validated_data['email'],
            'access': validated_data['access'],
            'refresh': validated_data['refresh'],
        }

    # Для аутентификации метод update обычно не используется.
    def update(self, instance, validated_data):
        pass


class VacancySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'
        # Если вы хотите разрешить только определенные поля для записи, используйте read_only_fields
        # read_only_fields = ('published_at', 'is_active',)


class VacancyResponseSerializer(serializers.ModelSerializer):
    worker = serializers.SerializerMethodField()

    class Meta:
        model = VacancyResponse
        fields = ['id', 'vacancy', 'worker', 'is_favorite', 'responded_at', 'status']

    def get_worker(self, obj):
        return {
            'id': obj.worker.id,
            'username': obj.worker.username,
            'email': obj.worker.email,
        }


class RespondedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'status']  # добавь, что нужно