from django.core.mail import send_mail


def send_activation_email(self, user):
    link = 'https://example.com/activate/{user_id}/{token}'.format(
        user_id=user.id,
        token=user.auth_token.key)

    # отправляем письмо
    send_mail(
        'Подтверждение регистрации',
        f'Привет, {user.email}! Для активации вашего аккаунта пройдите по ссылке: {link}',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )