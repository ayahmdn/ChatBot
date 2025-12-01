from django.shortcuts import render

import requests
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests, os, time

# Load token
HF_API_KEY = os.getenv("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")
HF_API_URL = "https://router.huggingface.co/hf-inference/models"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


#translation
@api_view(['POST'])
def translate_text(request):
    """
    POST payload:
    {
        "text": "Hello world",
        "source": "en",
        "target": "ar"
    }
    """
    data = request.data
    text = data.get("text", "")
    src = data.get("source", "").lower()
    tgt = data.get("target", "").lower()

    if not text or src not in ("en", "ar") or tgt not in ("en", "ar") or src == tgt:
        return Response(
            {"error": "Provide valid text and language pair (en <-> ar)"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Select the models
    model = "Helsinki-NLP/opus-mt-en-ar" if src == "en" else "Helsinki-NLP/opus-mt-ar-en"
    API_URL = f"https://router.huggingface.co/hf-inference/models/{model}"

    HF_API_KEY = os.getenv("HF_API_KEY")
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    try:
        start = time.time()
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        response_data = response.json()
        elapsed = time.time() - start

        if response.status_code == 200 and isinstance(response_data, list):
            translation = response_data[0].get("translation_text", "")
            return Response({
                "input": text,
                "translation": translation,
                "model": model,
                "time_s": round(elapsed, 2)
            })
        else:
            return Response({
                "error": response_data.get("error", "Unknown error"),
                "status": response.status_code
            }, status=response.status_code)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# SUMMARIZATION 
@api_view(['POST'])
def summarize_text(request):
    """
    POST payload:
    {
        "text": "Your long article or paragraph here...",
        "min_length": 30,
        "max_length": 150
    }
    """
    data = request.data
    text = data.get("text", "")
    if not text:
        return Response({"error": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

    min_len = int(data.get("min_length", 30))
    max_len = int(data.get("max_length", 150))

    # model: facebook/bart-large-cnn
    API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
    HF_API_KEY = os.getenv("HF_API_KEY")
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {
        "inputs": text,
        "parameters": {
            "min_length": min_len,
            "max_length": max_len,
            "do_sample": False
        }
    }

    try:
        start = time.time()
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        elapsed = round(time.time() - start, 2)

        if response.status_code == 200 and isinstance(result, list):
            summary = result[0].get("summary_text", "")
            return Response({
                "input_summary": summary,
                "model": "facebook/bart-large-cnn",
                "time_s": elapsed
            })
        else:
            return Response({
                "error": result.get("error", "Unknown error"),
                "status": response.status_code
            }, status=response.status_code)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)