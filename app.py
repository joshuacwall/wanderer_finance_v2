#!/usr/bin/env python3
"""
Main Gradio application for Wanderer Finance.

This module creates and launches the web interface for viewing stock picks,
analysis results, and performance evaluation.
"""

import sys
import gradio as gr

from app import current_picks, welcome, evaluation, current_passes
from src.config import config
from src.utils.logging_config import setup_logging, get_logger, configure_third_party_logging

# Configure logging
setup_logging(log_level="INFO", log_file="logs/app.log")
configure_third_party_logging()
logger = get_logger(__name__)


def create_gradio_interface() -> gr.Blocks:
    """
    Create the main Gradio interface with all tabs.

    Returns:
        Configured Gradio Blocks interface
    """
    logger.info("Creating Gradio interface")

    try:
        with gr.Blocks(
            title="Wanderer Finance - AI Stock Analysis",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .tab-nav {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            }
            """
        ) as demo:
            gr.Markdown(
                """
                # 🏃 Wanderer Finance
                ### AI-Powered Intraday Stock Analysis Platform
                """,
                elem_id="header"
            )

            with gr.Tabs():
                welcome.create_tab()
                current_picks.create_tab()
                current_passes.create_tab()
                evaluation.create_tab()

        logger.info("Gradio interface created successfully")
        return demo

    except Exception as e:
        logger.error(f"Error creating Gradio interface: {e}", exc_info=True)
        raise


def main() -> int:
    """
    Main function to launch the application.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting Wanderer Finance application")

        # Create the interface
        demo = create_gradio_interface()

        # Launch the interface
        logger.info("Launching Gradio interface")
        demo.launch(
            share=config.ui.gradio_share,
            debug=config.ui.gradio_debug,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )

        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nApplication stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error launching application: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)