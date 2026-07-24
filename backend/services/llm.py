import json
from groq import Groq
from config import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

def generate_text(prompt: str, system_prompt: str = "") -> str:
    if not groq_client or not settings.GROQ_API_KEY:
        return (
            "[DEV MODE] GROQ_API_KEY is missing. "
            "Please add GROQ_API_KEY to your .env file to generate live AI proposals with Groq."
        )
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=3000,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Error connecting to Groq API: {str(e)}"


def extract_products_from_text(text: str) -> list[dict]:
    if not groq_client or not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set. Cannot extract products from text.")

    system = (
        "You are a data extraction assistant. Extract product information from the "
        'following text. Return a JSON object with a "products" array. Each product '
        "must have these fields:\n"
        "- name (string, required)\n"
        '- sku (string, generate one if not found, e.g. "PROD-001")\n'
        "- price (number, 0 if not found)\n"
        "- category (string or null)\n"
        "- description (string or null)\n"
        "- name_ar (string or null, Arabic name if present)\n"
        "- description_ar (string or null, Arabic description if present)\n\n"
        "Rules:\n"
        "- Only include items that look like actual products\n"
        "- If a field is not found, use null for strings and 0 for price\n"
        "- Return ONLY valid JSON, no markdown fences\n"
        '- Format: {"products": [{...}, ...]}'
    )

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Extract products from this text:\n\n{text}"},
        ],
        max_tokens=3500,
        temperature=0.1,
    )

    raw = (response.choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    data = json.loads(raw)
    if isinstance(data, dict) and "products" in data:
        return data["products"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unexpected JSON structure from LLM: {type(data)}")


def generate_rag_proposal(
    client_name: str,
    client_request: str,
    rag_chunks: list[dict],
    language: str = "en",
    org_name: str = ""
) -> str:
    context_str = ""
    if rag_chunks:
        context_str = "\n\n".join(
            f"--- Document Source: {c['filename']} ---\n{c['content']}"
            for c in rag_chunks
        )
    else:
        context_str = "No specific uploaded company documents found."

    if language == "ar":
        system = (
            "أنت خبير كبار المبيعات واستشاري مقترحات تجارية. مهمتك هي كتابة عرض سعر احترافي، محدد ومقنع للغاية "
            "مبني مباشرة على متطلبات العميل وسياق المستندات المرفقة للشركة."
            "\nاستخدم تنسيق Markdown واكتُب بلغة عربية رسمية وسلسة مع العناوين التالية:\n"
            "# عرض سعر تجاري: [اسم العميل]\n"
            "## 1. الملخص التنفيذي\n"
            "## 2. فهم متطلبات واحتياجات العميل\n"
            "## 3. الحلول والتوصيات المقترحة (مستندة للمستندات)\n"
            "## 4. نطاق العمل وخطة التنفيذ\n"
            "## 5. التكلفة والأسعار المقدرة\n"
            "## 6. الخطوات القادمة ودعوة للعمل (Call to Action)"
        )
        prompt = (
            f"اسم الشركة المزودة: {org_name or 'شركتنا'}\n"
            f"اسم العميل: {client_name}\n"
            f"متطلبات وطلب العميل: {client_request}\n\n"
            f"المعلومات والسياق المستخرج من مستندات الشركة (RAG Context):\n{context_str}\n\n"
            f"قم بكتابة المقترح المطلوب بشكل متكامل ومكتمل في Markdown."
        )
    else:
        system = (
            "You are a Senior Enterprise Sales Proposal Consultant. Your task is to write a highly compelling, "
            "structured, professional B2B sales proposal tailored to the client's demands using the uploaded company context."
            "\nUse clean Markdown with executive formatting and clear section headers:\n"
            "# Business Proposal: [Client Name]\n"
            "## 1. Executive Summary\n"
            "## 2. Customer Needs & Problem Statement\n"
            "## 3. Proposed Solutions & Technical Scope\n"
            "## 4. Implementation Timeline & Deliverables\n"
            "## 5. Investment & Commercial Terms\n"
            "## 6. Next Steps & Call to Action"
        )
        prompt = (
            f"Provider Company: {org_name or 'Our Organization'}\n"
            f"Client Name: {client_name}\n"
            f"Customer Demands & Requirements: {client_request}\n\n"
            f"Company Knowledge Base Context (RAG Retrieved Documents):\n{context_str}\n\n"
            f"Generate a comprehensive, persuasive proposal in Markdown."
        )

    return generate_text(prompt, system)


def chat_edit_proposal(
    current_content: str,
    user_message: str,
    chat_history: list[dict],
    language: str = "en"
) -> tuple[str, str]:
    """
    Conversational AI editor:
    Takes current proposal content and chat history, applies user's request,
    and returns a tuple of (updated_proposal_markdown, ai_explanation_response).
    """
    if not groq_client or not settings.GROQ_API_KEY:
        return current_content, "GROQ_API_KEY is not configured."

    system = (
        "You are an interactive AI Sales Proposal Assistant powered by Groq Llama 3.3. "
        "You help employees refine, expand, translate, or customize sales proposals live in chat.\n\n"
        "Respond ONLY in valid JSON format with two keys:\n"
        '1. "ai_response": A friendly, helpful, executive chat response explaining what changes were made.\n'
        '2. "updated_proposal": The complete revised proposal in Markdown format incorporating the user request.\n\n'
        'JSON format example:\n'
        '{"ai_response": "I have added the 10% volume discount section...", "updated_proposal": "# Business Proposal..."}'
    )

    history_str = ""
    for msg in chat_history[-6:]:
        role = "Employee" if msg.get("sender") == "user" else "AI Assistant"
        history_str += f"{role}: {msg.get('message')}\n"

    user_prompt = (
        f"CURRENT PROPOSAL MARKDOWN:\n{current_content}\n\n"
        f"PAST CHAT CONVERSATION:\n{history_str}\n"
        f"EMPLOYEE LATEST REQUEST:\n{user_message}\n\n"
        f"Return ONLY valid JSON with 'ai_response' and 'updated_proposal'."
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=3800,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content or ""
        data = json.loads(raw)
        
        ai_resp = data.get("ai_response", "I updated the proposal based on your request.")
        updated_prop = data.get("updated_proposal", current_content)
        return updated_prop, ai_resp

    except Exception as e:
        # Fallback if json parsing or model call fails
        fallback_prompt = (
            f"Revise this proposal according to request: {user_message}\n\nProposal:\n{current_content}"
        )
        new_text = generate_text(fallback_prompt, "You are a professional proposal editor. Return updated proposal markdown.")
        return new_text, f"I have revised the proposal according to your feedback."
