import os
import sys
import signal
import logging
import argparse
from typing import Dict, Any
from realnet.core.config import load_config
from realnet.runner.mqtt.runner import MQTTRunner
from realnet.shell import ProtoCmd

logger = logging.getLogger(__name__)

class Runner(ProtoCmd):
    def __init__(self):
        super().__init__('runner',
                        'Run the MQTT message handler',
                        lambda args: main())

    def add_arguments(self, parser):
        pass

def load_script() -> str:
    """Load the runner script."""
    script_path = os.environ.get('REALNET_RUNNER_SCRIPT', '/app/script.py')
    try:
        with open(script_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load script from {script_path}: {str(e)}")
        return None

def main():
    """Main runner entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Load configuration
        config = load_config()
        
        # Create runner
        runner = MQTTRunner(config)
        
        # Load initial script
        script = load_script()
        if script:
            runner._handle_update_script({'script': script})
        
        # Handle shutdown gracefully
        def signal_handler(signum, frame):
            logger.info("Shutdown signal received")
            runner.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start runner
        runner.start()
        
        # Keep running until interrupted
        signal.pause()
        
    except Exception as e:
        logger.error(f"Runner failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
