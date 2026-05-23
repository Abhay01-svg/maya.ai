from flask import Flask, request, jsonify
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing Maya modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../maya_ai')))

try:
    from modules.brain import brain
    logger.info("✅ Successfully integrated with Maya Brain")
    # Try to import model cache for clearing cached responses
    try:
        from modules.models import model_cache
    except Exception:
        model_cache = None
except ImportError as e:
    logger.error(f"❌ Could not import Maya Brain: {e}")
    # Fallback path check
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'maya_ai')))
    try:
        from modules.brain import brain
        logger.info("✅ Successfully integrated with Maya Brain (fallback path)")
    except:
        logger.error("❌ Critical: Brain module still not found.")
        brain = None

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_voice():
    data = request.json
    text = data.get('text', '')
    logger.info(f"🎙️ Processing voice input: {text}")
    
    if brain:
        try:
            # Maya's brain handles intent routing, tools, and local models
            response = brain.process_query(text)
            
            # Extract the Hinglish response for the VUI
            reply = response.get('hinglish_response', 'Maaf kijiye bhai, main samajh nahi paayi.')
            
            logger.info(f"🤖 Maya Reply: {reply}")
            return jsonify({
                "status": "success",
                "reply": reply,
                "intent": response.get('intent', 'unknown'),
                "success": response.get('success', True)
            })
        except Exception as e:
            logger.error(f"❌ Brain execution error: {e}")
            return jsonify({
                "status": "error",
                "reply": "Dimaag mein kuch problem ho gayi hai bhai.",
                "error": str(e)
            })
    
    return jsonify({
        "status": "mock",
        "reply": f"Main abhi limited mode mein hoon, par aapne kaha: {text}",
        "intent": "general"
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check for the Python brain service."""
    try:
        return jsonify({"status": "ok", "service": "polyglot_python_brain"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/cache/clear', methods=['POST', 'GET'])
def clear_cache():
    """Clear model cache to remove verbose cached responses."""
    try:
        cleared = False
        if 'model_cache' in globals() and model_cache is not None:
            model_cache.clear()
            cleared = True
        # Also clear any brain-level cache if present
        try:
            if brain and hasattr(brain, 'cache'):
                brain.cache.clear()
                cleared = True
        except Exception:
            pass

        if cleared:
            return jsonify({"status": "ok", "cleared": True})
        else:
            return jsonify({"status": "noop", "cleared": False, "reason": "no cache object found"}), 404
    except Exception as e:
        logger.error(f"❌ Cache clear error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Polyglot Python Brain starting on port 5001...")
    app.run(port=5001, debug=False)
