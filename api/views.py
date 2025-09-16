from django.http import HttpRequest, JsonResponse
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import Call, ChatMessage
from utils.ai import analyze_message

import json

@csrf_exempt
def send(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        text = payload.get("message", "").strip()
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    if not text:
        return JsonResponse({"error": "empty message"}, status=400)
    
    qs = ChatMessage.objects.filter(user=request.user).order_by("-created_at")[:20]
    history = []
    for msg in reversed(qs):
        history.append({"role": "user", "content": msg.content})

    result = analyze_message(text, user_id=str(request.user.id), history=history)

    ChatMessage.objects.create(user=request.user, role="user", content=text)
    ChatMessage.objects.create(user=request.user, role="assistant", content=result["reply_to_user"])

    if result["risk_level"] in ("Critical", "High", "Medium"):
        Call.objects.create(
            target=request.user,
            message=text,
            risk_level=result["risk_level"],
            explanation=result["explanation"],
            recommended_action=result["recommended_action"],
            reply_to_user=result["reply_to_user"]
        )

    return JsonResponse({
        "reply": result["reply_to_user"],
        "risk_level": result["risk_level"],
        "risk_confidence": result["risk_confidence"],
        "explanation": result["explanation"],
        "recommended_action": result["recommended_action"],
    })
