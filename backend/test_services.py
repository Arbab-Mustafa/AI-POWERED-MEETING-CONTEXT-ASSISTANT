"""
Test script to verify AI context generation and services.
"""

import asyncio
import httpx
from datetime import datetime, timedelta

# Test Ollama connection
async def test_ollama():
    """Test if Ollama is running and responsive."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Ollama is running!")
                print(f"Available models: {models}")
                return True
            else:
                print(f"❌ Ollama returned status code: {response.status_code}")
                return False
    except httpx.ConnectError:
        print("❌ Ollama is not running. Start it with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False

# Test AI context generation
async def test_ai_generation():
    """Test AI context generation with a sample meeting."""
    from app.services.ai_service import ai_generator
    
    print("\n🤖 Testing AI Context Generation...")
    
    context = await ai_generator.generate_meeting_context(
        title="Weekly Team Sync",
        description="Discuss project progress and blockers",
        attendees=["alice@example.com", "bob@example.com"],
        start_time=datetime.now() + timedelta(hours=2)
    )
    
    print(f"✅ AI Context Generated!")
    print(f"Meeting Type: {context.get('meeting_type')}")
    print(f"Brief: {context.get('brief')}")
    print(f"Key Topics: {context.get('topics')}")
    print(f"Checklist: {context.get('checklist')}")
    print(f"Confidence: {context.get('confidence')}%")

# Test backend API
async def test_backend_api():
    """Test if backend API is responsive."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend API is running!")
                print(f"Status: {data.get('status')}")
                print(f"Environment: {data.get('environment')}")
                return True
            else:
                print(f"❌ Backend API returned status: {response.status_code}")
                return False
    except httpx.ConnectError:
        print("❌ Backend API is not running. Start it with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("ContextMeet - Service Integration Tests")
    print("=" * 60)
    
    # Test 1: Backend API
    print("\n1️⃣ Testing Backend API...")
    backend_ok = await test_backend_api()
    
    # Test 2: Ollama
    print("\n2️⃣ Testing Ollama/Mistral...")
    ollama_ok = await test_ollama()
    
    # Test 3: AI Generation (only if Ollama is running)
    if ollama_ok:
        try:
            await test_ai_generation()
        except Exception as e:
            print(f"❌ AI generation test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Backend API: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Ollama/Mistral: {'✅ PASS' if ollama_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if backend_ok and ollama_ok:
        print("\n🎉 All services are ready! Your ContextMeet backend is fully operational.")
        print("\n📝 Next steps:")
        print("   1. Open http://localhost:8000/docs to test API endpoints")
        print("   2. Register a test user via POST /api/v1/auth/register")
        print("   3. Create a meeting and generate AI context")
        print("   4. Set up Google Calendar sync (optional)")
    else:
        print("\n⚠️ Some services need attention:")
        if not backend_ok:
            print("   • Start backend: cd backend && uvicorn app.main:app --reload")
        if not ollama_ok:
            print("   • Start Ollama: ollama serve")

if __name__ == "__main__":
    asyncio.run(main())
