def login(func):
    def wrapper(request):
        if request.user.is_authenticated:
            print('пользователь не залогинился')
        else:
            func(request)
    return wrapper