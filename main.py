#!/usr/bin/env python3
"""
LYRIA - AI-Powered Video Narration & Enhancement Pipeline
Main entry point for the application

Usage:
    python main.py              # Run full pipeline (phases 1-5)
    python main.py --phases 1,2,3  # Run specific phases
    python main.py --help       # Show help
"""

import sys
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import LyriaConfig
from orchestrator import create_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lyria.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="LYRIA - AI Video Narration & Enhancement Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run full pipeline (phases 1-5)
  %(prog)s --phases 1,2,3     # Run specific phases
  %(prog)s --phases 1,2       # Run ingest + analysis only
  %(prog)s --config /path/to/.env  # Use custom .env file
        """
    )
    
    parser.add_argument(
        "--phases",
        type=str,
        default="1,2,3,4,5",
        help="Comma-separated phase numbers to run (1-5). Default: 1,2,3,4,5"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=".env",
        help="Path to .env configuration file"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="Override VIDEO_SOURCE_URL from .env"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Override OUTPUT_DIR from .env"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = LyriaConfig.from_env()
        
        # Override values if provided
        if args.url:
            config.video_source_url = args.url
            logger.info(f"Overriding video URL: {args.url}")
        
        if args.output:
            config.output_dir = Path(args.output)
            config.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Overriding output directory: {args.output}")
        
        # Validate configuration
        if not config.qwen.api_key:
            logger.error("DASHSCOPE_API_KEY not set in .env file")
            sys.exit(1)
        
        if not config.video_source_url:
            logger.error("VIDEO_SOURCE_URL not set in .env file")
            sys.exit(1)
        
        logger.info(f"Configuration loaded. Output: {config.output_dir}")
        
        # Parse phases
        try:
            phases = [int(p.strip()) for p in args.phases.split(",")]
            phases = [p for p in phases if 1 <= p <= 5]
        except ValueError:
            logger.error(f"Invalid phases format: {args.phases}")
            sys.exit(1)
        
        if not phases:
            logger.error("No valid phases specified")
            sys.exit(1)
        
        logger.info(f"Running phases: {phases}")
        
        # Create and run orchestrator
        orchestrator = create_orchestrator(config)
        
        if set(phases) == {1, 2, 3, 4, 5}:
            result = orchestrator.run_full_pipeline()
        else:
            result = orchestrator.run_partial_pipeline(phases)
        
        # Print final result
        logger.info("\n" + "=" * 60)
        logger.info("EXECUTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Output directory: {config.output_dir}")
        logger.info(f"Status: {result['status']}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
