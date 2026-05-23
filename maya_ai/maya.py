"""
🤖 MAYA AI - Advanced Personal Desktop Assistant
Smart, efficient, multilingual (Hinglish), self-learning AI for Windows PC

Main Launcher and CLI Interface
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
from config import DEBUG_MODE, LOGS_DIR, OWNER_NAME

# Set console encoding to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"maya_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import core modules
from modules.brain import brain
from modules.voice import voice_interface
from modules.memory import memory

class MayaCLI:
    """Command-line interface for Maya AI"""
    
    def __init__(self):
        self.running = True
        self.commands = {
            "chat": self.cmd_chat,
            "voice": self.cmd_voice,
            "plan": self.cmd_plan,
            "planner": self.cmd_plan,
            "status": self.cmd_status,
            "memory": self.cmd_memory,
            "stats": self.cmd_stats,
            "settings": self.cmd_settings,
            "export": self.cmd_export,
            "clear": self.cmd_clear,
            "shutdown": self.cmd_shutdown,
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }
    
    # ==================== COMMANDS ====================
    
    def cmd_chat(self, args):
        """Chat with Maya"""
        if args:
            query = " ".join(args)
        else:
            query = input("💬 You: ").strip()
        
        if not query:
            return
        
        print("\n⏳ Processing...")
        response = brain.process_query(query)
        
        if response["success"]:
            result = response['hinglish_response']
            print(f"\n🤖 Maya: {result}\n")
            
            # Auto speak in voice mode (no prompt needed)
            if voice_interface.enabled:
                voice_interface.speak_response(result)
        else:
            print(f"\n❌ Error: {response['hinglish_response']}\n")
    
    def cmd_voice(self, args):
        """Enter voice mode with instant brain connection"""
        import subprocess
        
        print("\n🎤 Entering voice mode...")
        print("Say: 'Hey Maya' followed by your command")
        print("Say: 'c' or 'taskkill' for instant fast mode")
        print("Say: 'exit' to quit voice mode\n")
        
        # Use VUI-specific greeting (no username mention)
        greeting = brain.get_smart_greeting(vui_mode=True)
        print(f"🤖 {greeting}")
        voice_interface.speak_response(greeting)
        
        def process_voice_command(query):
            """Process voice command and show results in VUI"""
            query_lower = query.lower().strip()
            
            # Fast mode: 'c' command kills Ollama models for instant response
            if query_lower == 'c' or query_lower == 'taskkill':
                try:
                    subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                                 capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    fast_msg = "✅ Fast mode active. Ollama models killed to save RAM."
                    print(f"\n⚡ {fast_msg}\n")
                    voice_interface.speak_response(fast_msg)
                    return fast_msg
                except Exception as e:
                    err_msg = f"⚠️ Fast mode error: {e}"
                    print(f"\n{err_msg}\n")
                    voice_interface.speak_response(err_msg)
                    return err_msg
            
            # Regular processing
            print(f"\n📝 Query: {query}")
            print("⏳ Processing...")
            
            try:
                response = brain.process_query(query)
                
                if response["success"]:
                    result = response['hinglish_response']
                    # Remove any remaining username mentions for VUI
                    result = result.replace(f"{OWNER_NAME}, ", "").replace(OWNER_NAME, "")
                    print(f"\n🤖 Maya: {result}\n")
                    
                    # Always speak response in VUI mode (instant reply)
                    voice_interface.speak_response(result, async_mode=False)
                    return result
                else:
                    error_msg = response['hinglish_response']
                    print(f"\n❌ Error: {error_msg}\n")
                    voice_interface.speak_response(f"Sorry, {error_msg}")
                    return error_msg
                    
            except Exception as e:
                err_msg = f"Processing error: {str(e)}"
                print(f"\n❌ {err_msg}\n")
                voice_interface.speak_response("Sorry, kuch error ho gaya")
                return err_msg
        
        try:
            voice_interface.interactive_mode(process_voice_command)
        except KeyboardInterrupt:
            print("\n👋 Voice mode ended")
        except Exception as e:
            print(f"\n❌ VUI Error: {e}")
            print("👋 Voice mode ended due to error")
    
    def cmd_plan(self, args):
        """Maya Planner Core - Task planning and workflow management"""
        from modules.planner import planner, PlanStatus, TaskPriority
        
        if not args:
            print("""
🎯 MAYA PLANNER CORE - Workflow Intelligence System

Commands:
  plan create <name> <goal>     - Create new plan
  plan list                     - List all plans
  plan list active              - List active plans
  plan show <plan_id>           - Show plan details
  plan add-step <plan_id> <desc> <action>  - Add step to plan
  plan execute <plan_id>        - Execute entire plan
  plan delete <plan_id>         - Delete plan
  plan history                  - Show execution history

Examples:
  maya plan create "Morning Routine" "Start my day efficiently"
  maya plan add-step abc123 "Open Chrome" "open_chrome"
  maya plan execute abc123
            """)
            return
        
        cmd = args[0].lower()
        
        if cmd == "create" and len(args) >= 3:
            name = args[1]
            goal = " ".join(args[2:])
            plan = planner.create_plan(name, f"Plan for: {goal}", goal)
            print(f"\n✅ Created plan: {plan.name}")
            print(f"   Plan ID: {plan.plan_id}")
            print(f"   Goal: {plan.goal}")
            print("\n💡 Next: Add steps with 'plan add-step'")
            
        elif cmd == "list":
            status_filter = args[1] if len(args) > 1 else None
            if status_filter == "active":
                plans = planner.list_plans(status=PlanStatus.IN_PROGRESS)
            else:
                plans = planner.list_plans()
            
            if plans:
                print("\n📋 Plans:")
                for p in plans:
                    status_emoji = {"completed": "✅", "in_progress": "🔄", 
                                  "pending": "⏳", "failed": "❌"}.get(p['status'], "⏳")
                    print(f"  {status_emoji} [{p['plan_id']}] {p['name']} ({p['progress']:.0f}%)")
                    print(f"     Goal: {p['goal']}")
            else:
                print("\n📭 No plans found")
                
        elif cmd == "show" and len(args) > 1:
            plan_id = args[1]
            plan = planner.get_plan(plan_id)
            if plan:
                print(f"\n📋 Plan: {plan.name} [{plan.plan_id}]")
                print(f"   Goal: {plan.goal}")
                print(f"   Status: {plan.status.value}")
                print(f"   Progress: {plan.progress:.0f}%")
                print(f"   Created: {plan.created_at.strftime('%Y-%m-%d %H:%M')}")
                if plan.steps:
                    print("\n   Steps:")
                    for step in plan.steps:
                        status_emoji = {"completed": "✅", "in_progress": "🔄", 
                                      "pending": "⏳", "failed": "❌"}.get(step.status.value, "⏳")
                        print(f"     {status_emoji} {step.step_id}. {step.description}")
                else:
                    print("\n   No steps yet. Add with 'plan add-step'")
            else:
                print(f"❌ Plan not found: {plan_id}")
                
        elif cmd == "add-step" and len(args) >= 4:
            plan_id = args[1]
            description = args[2]
            action = args[3]
            
            plan = planner.get_plan(plan_id)
            if plan:
                step = plan.add_step(description, action)
                planner._save_plan(plan)
                print(f"✅ Added step {step.step_id}: {description}")
            else:
                print(f"❌ Plan not found: {plan_id}")
                
        elif cmd == "execute" and len(args) > 1:
            plan_id = args[1]
            print(f"\n🚀 Executing plan: {plan_id}")
            result = planner.execute_plan(plan_id)
            
            if result['success']:
                print(f"✅ Plan completed!")
                print(f"   Steps executed: {result['completed_steps']}/{result['total_steps']}")
            else:
                print(f"❌ Plan failed: {result.get('error', 'Unknown error')}")
                
        elif cmd == "delete" and len(args) > 1:
            plan_id = args[1]
            if planner.delete_plan(plan_id):
                print(f"✅ Deleted plan: {plan_id}")
            else:
                print(f"❌ Failed to delete plan: {plan_id}")
                
        elif cmd == "history":
            history = planner.get_execution_history()
            if history:
                print("\n📜 Execution History:")
                for h in history[:10]:
                    status_emoji = "✅" if h['status'] == 'completed' else "❌"
                    print(f"  {status_emoji} [{h['plan_id']}] Step {h['step_id']}: {h['action']}")
            else:
                print("\n📭 No execution history")
    
    def cmd_status(self, args):
        """Show system status"""
        print("\n" + brain.get_system_status())
    
    def cmd_memory(self, args):
        """Manage memory"""
        if not args:
            print("\n📚 Memory Commands:")
            print("  maya memory list - Show all preferences")
            print("  maya memory export <file> - Export memory to JSON")
            print("  maya memory clear - Clear chat history")
            print("  maya memory stats - Show memory stats")
            return
        
        cmd = args[0].lower()
        
        if cmd == "list":
            prefs = memory.get_all_preferences()
            if prefs:
                print("\n📝 Preferences:")
                for key, value in prefs.items():
                    print(f"  {key}: {value}")
            else:
                print("\n📭 No preferences saved")
        
        elif cmd == "export" and len(args) > 1:
            filepath = args[1]
            if memory.export_memory(filepath):
                print(f"✅ Memory exported to {filepath}")
            else:
                print("❌ Export failed")
        
        elif cmd == "stats":
            stats = brain.get_statistics()
            print(f"\n📊 Memory Stats:")
            print(f"  Chat history: {stats['memory_stats']['chat_history']}")
            print(f"  Preferences: {stats['memory_stats']['preferences']}")
            print(f"  Routines: {stats['memory_stats']['routines']}")
    
    def cmd_stats(self, args):
        """Show performance statistics"""
        stats = brain.get_statistics()
        print(f"""
📊 Performance Statistics:
  Total queries: {stats['total_queries']}
  Avg response time: {stats['avg_response_time']:.2f}s
  Model efficiency: {stats['model_efficiency']['model_ratio']}
  Chat history: {stats['memory_stats']['chat_history']}
        """)
    
    def cmd_settings(self, args):
        """Manage settings"""
        from config import (DEBUG_MODE, AUTO_LEARN, HINGLISH_MODE, 
                          VOICE_MODE, GUI_MODE, OWNER_ONLY_MODE)
        
        print(f"""
⚙️  Current Settings:
  Debug mode: {'✅' if DEBUG_MODE else '❌'}
  Auto-learn: {'✅' if AUTO_LEARN else '❌'}
  Hinglish mode: {'✅' if HINGLISH_MODE else '❌'}
  Voice mode: {'✅' if VOICE_MODE else '❌'}
  GUI mode: {'✅' if GUI_MODE else '❌'}
  Owner-only: {'✅' if OWNER_ONLY_MODE else '❌'}
        """)
    
    def cmd_export(self, args):
        """Export memory"""
        if len(args) > 1:
            filepath = args[1]
        else:
            filepath = f"maya_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if memory.export_memory(filepath):
            print(f"✅ Memory exported to {filepath}")
        else:
            print("❌ Export failed")
    
    def cmd_clear(self, args):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def cmd_shutdown(self, args):
        """Shutdown PC"""
        confirm = input("⚠️  Shutdown PC? (yes/no): ").lower().strip()
        if confirm == "yes":
            result = brain.process_query("shutdown pc")
            print(result['hinglish_response'])
        else:
            print("❌ Cancelled")
    
    def cmd_help(self, args):
        """Show help"""
        print("""
🤖 MAYA AI - Commands:

General:
  chat            - Chat with Maya
  voice           - Enter voice mode
  plan/planner    - Task planning & workflow management
  status          - Show system status
  stats           - Show performance statistics
  settings        - Show current settings
  clear           - Clear screen
  exit/quit       - Exit Maya

Planner (Maya Planner Core):
  plan create <name> <goal>  - Create new plan
  plan list                  - List all plans
  plan show <plan_id>        - Show plan details
  plan add-step <id> <desc> <action>  - Add step to plan
  plan execute <plan_id>     - Execute plan
  plan delete <plan_id>      - Delete plan
  plan history               - Show execution history

Memory:
  memory list     - Show all preferences
  memory export   - Export memory
  memory stats    - Show memory statistics
  memory clear    - Clear history

System:
  shutdown        - Shutdown PC
  help            - Show this help
        """)
        print("""
Examples:
  maya chat "What is 25*89?"
  maya chat "Open chrome"
  maya chat "Weather in Delhi"
  maya voice       - Use voice commands
        """)
    
    def cmd_exit(self, args):
        """Exit Maya"""
        print("\n👋 Thank you for using Maya AI!")
        print("🌙 See you next time!\n")
        self.running = False
    
    # ==================== MAIN LOOP ====================
    
    def run_interactive(self):
        """Run interactive CLI"""
        self.print_banner()
        # CLI mode uses username greeting, VUI mode doesn't
        print(f"\n{brain.get_smart_greeting(vui_mode=False)}\n")
        
        while self.running:
            try:
                user_input = input("Maya> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    # Treat as query
                    self.cmd_chat([user_input])
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type 'exit' to quit.")
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                print(f"❌ Error: {e}")
    
    def run_single_query(self, query: str):
        """Run single query and exit"""
        response = brain.process_query(query)
        print(response['hinglish_response'])
    
    def print_banner(self):
        """Print ASCII banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🤖 MAYA AI - Personal Assistant              ║
║            Smart • Fast • Intelligent • Multilingual      ║
║                                                           ║
║  Type 'help' for commands or start chatting with Maya!   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        print(banner)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Maya AI - Personal Desktop Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python maya.py                              # Interactive mode
  python maya.py "What is 25*89?"             # Single query
  python maya.py "Open chrome"                # Command
  python maya.py --voice                      # Voice mode
  python maya.py --status                     # Show status
        """
    )
    
    parser.add_argument('query', nargs='*', help='Query for Maya')
    parser.add_argument('--voice', action='store_true', help='Start in voice mode')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--help-commands', action='store_true', help='Show all commands')
    parser.add_argument('--version', action='version', version='Maya AI v1.0')
    
    args = parser.parse_args()
    
    # Create CLI
    cli = MayaCLI()
    
    # Handle different modes
    if args.help_commands:
        cli.cmd_help([])
    elif args.status:
        cli.cmd_status([])
    elif args.stats:
        cli.cmd_stats([])
    elif args.voice:
        cli.cmd_voice([])
    elif args.query:
        # Single query mode
        query = " ".join(args.query)
        cli.run_single_query(query)
    else:
        # Interactive mode
        cli.run_interactive()


if __name__ == "__main__":
    print("🚀 Starting Maya AI...\n")
    main()
