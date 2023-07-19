from django.http import HttpResponse, JsonResponse


class MaintenanceModeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查服务器是否处于维护模式
        maintenance_mode = False  # 我认为这个应该做个全局变量 来判断是否服务器在维护状态
        #过载的情况太难写了 我还没学到
        ans = {
            "success": 'false',
            "type": 2,
            "message": "HTTP response with code 503",
            "details": {
                "status": 503
            }
        }
        if maintenance_mode:
            # 返回维护模式下的响应
            return JsonResponse(ans, status=200)

        # 继续处理其他请求

        response = self.get_response(request)

        return response