from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        if response is not None and response.exception:
            return super().render(data, accepted_media_type, renderer_context)

        view = renderer_context.get("view")
        request = renderer_context.get("request")
        messages = getattr(view, "success_messages", {})
        message = messages.get(request.method, "") if request is not None else ""

        payload = {"success": True, "message": message, "data": data}
        return super().render(payload, accepted_media_type, renderer_context)
