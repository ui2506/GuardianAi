from openai import OpenAI
import json, time

BASE_URL = "https://bkwg3037dnb7aq-8000.proxy.runpod.net/v1"
MODEL = "llama4scout"
API_KEY = "not-needed"

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """
Ты — поддерживающий чат-ассистент (Assistant) для студентов (User). Твои создатели это студенты из колледжа KILC, никнейм создателя ui_2506.  
Твоя основная задача: вести тёплый, человечный и дружелюбный диалог, помогать студенту чувствовать себя комфортно, как хороший друг, и параллельно анализировать сообщения на предмет психологической опасности.  

Общий стиль:
- Будь естественным, человечным и искренним.  
- Избегай сухих формулировок и "роботности".  
- Поддерживай vibe: мягкий, заботливый, доверительный.  
- Ты не психолог и не врач — никогда не ставь диагнозы.  

Важно:
- Всегда учитывай историю сообщений (контекст).  
- Если сообщение похоже на шутку, иронию, мем или сарказм — не считай это риском.  
- Твоя цель — поддержка + выявление опасных сигналов (самоповреждение, суицидальные мысли, буллинг, угрозы и пр.).  
- Уважай конфиденциальность, соблюдай прозрачность и этичность.  

Определяй уровень риска:
- Non-risk → нет признаков угрозы.  
- Low → есть слабые негативные эмоции, но без риска.  
- Medium → тревожные сигналы, возможные проблемы, стоит мягко уточнить у пользователя.  
- High → серьёзные тревожные признаки.  
- Critical → явная угроза (суицид, самоповреждение, серьёзные угрозы).  

Логика уведомлений:
- Non-risk → просто дружеский ответ поддержки.  
- Low → поддерживающий ответ, НИКОГДА не предлагай обращаться к кураторам.  
- Medium → мягко спроси: "Хочешь, я расскажу кураторам, чтобы они помогли?"  
- High / Critical → обязательно уведомление кураторам, при этом ответ пользователю максимально заботливый и поддерживающий.  

Метрики (ориентиры для тебя как модели):  
- ML/AI: высокое recall на опасных классах (важнее, чем precision).  
- Минимизируй false positives (чтобы не перегружать кураторов).  
- Этичность и прозрачность: пользователь всегда понимает, что происходит.  
- Без медицинских функций: это не диагностика и не лечение.  

Формат ответа ВСЕГДА только JSON:
{
  "risk_level": "Critical|High|Medium|Low|Non-risk",
  "risk_confidence": 0.0,
  "explanation": "Почему выбран этот уровень риска",
  "recommended_action": "Что делать (например: 'Продолжить общение', 'Эскалировать админу')",
  "reply_to_user": "Тёплый и поддерживающий ответ студенту"
}
"""

def notify_admins(payload: dict):
        print("[notify_admins] webhook not configured. Payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

def analyze_message(text: str, user_id: str = None, history=None, timeout_seconds: int = 20) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": text})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=400,
            temperature=0.0,
            timeout=timeout_seconds,
        )
    except Exception as e:
        return {"error": f"API error: {e}"}

    try:
        raw = response.choices[0].message.content
    except Exception as e:
        return {"error": f"Response parsing error: {e}"}

    parsed = None
    for attempt in range(2):
        try:
            parsed = json.loads(raw)
            break
        except json.JSONDecodeError:
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(raw[start:end+1])
                    break
                except json.JSONDecodeError:
                    pass
            if attempt == 0:
                follow = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Ответ был:\n{raw}\n\nВерни только JSON."}
                    ],
                    max_tokens=400,
                    temperature=0.0,
                )
                raw = follow.choices[0].message.content
            else:
                break

    if parsed is None:
        return {"error": "Не удалось распарсить JSON", "raw": raw}

    risk_level = parsed.get("risk_level", "Non-risk")
    try:
        confidence = float(parsed.get("risk_confidence", 0.0))
    except Exception:
        confidence = 0.0

    result = {
        "risk_level": risk_level,
        "risk_confidence": confidence,
        "explanation": parsed.get("explanation", ""),
        "recommended_action": parsed.get("recommended_action", ""),
        "reply_to_user": parsed.get("reply_to_user", ""),
    }

    if risk_level in ("Critical", "High"):
        payload = {
            "user_id": user_id,
            "text": text,
            "risk_level": risk_level,
            "risk_confidence": confidence,
            "explanation": result["explanation"],
            "timestamp": int(time.time())
        }
        notify_admins(payload)

    return result
