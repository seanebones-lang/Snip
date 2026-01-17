"""
Test script for X.AI TTS integration
Run with: python -m backend.test_xai_tts
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import generate_xai_tts_audio, convert_pcm_to_wav


async def test_tts():
    """Test X.AI TTS generation"""
    # Get API key from environment
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("ERROR: XAI_API_KEY environment variable not set")
        print("Set it with: export XAI_API_KEY='your-api-key-here'")
        return
    
    test_text = "Hello! This is a test of the X.AI text-to-speech integration."
    print(f"Testing TTS with text: {test_text}")
    print("This may take a few seconds...")
    
    try:
        # Generate audio
        pcm_audio = await generate_xai_tts_audio(
            text=test_text,
            api_key=api_key,
            voice="Ara"
        )
        
        if pcm_audio:
            print(f"✅ Success! Generated {len(pcm_audio)} bytes of PCM audio")
            
            # Convert to WAV
            wav_audio = convert_pcm_to_wav(pcm_audio)
            print(f"✅ Converted to WAV: {len(wav_audio)} bytes")
            
            # Save to file for testing
            output_file = "test_output.wav"
            with open(output_file, "wb") as f:
                f.write(wav_audio)
            print(f"✅ Saved audio to: {output_file}")
            print(f"   You can play this file to verify the audio quality")
        else:
            print("❌ Failed to generate audio")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_tts())
