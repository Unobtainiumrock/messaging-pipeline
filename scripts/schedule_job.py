#!/usr/bin/env python3
"""
Script to schedule the communication centralizer to run periodically.
"""
import sys
import logging
import argparse
from crontab import CronTab
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scheduler")


def schedule_job(frequency: str = "hourly") -> bool:
    """
    Schedule the communication centralizer to run at specified frequency.

    Args:
        frequency: Frequency to run (hourly, daily, custom)

    Returns:
        True if scheduled successfully, False otherwise
    """
    try:
        # Get current user crontab
        cron = CronTab(user=True)

        # Get project directory (assuming script is in project/scripts/)
        project_dir = Path(__file__).parent.parent.absolute()
        logger.info(f"Project directory: {project_dir}")

        # Define the command to run
        python_path = f"{project_dir}/venv/bin/python"
        script_path = f"{project_dir}/src/main.py"
        log_path = f"{project_dir}/logs/cron_run.log"
        command = f"cd {project_dir} && {python_path} {script_path} >> {log_path} 2>&1"

        # Remove existing jobs for this script
        for job in cron.find_comment("communication-centralizer"):
            cron.remove(job)
            logger.info("Removed existing cron job")

        # Create new job
        job = cron.new(command=command, comment="communication-centralizer")

        # Set schedule based on frequency
        if frequency == "hourly":
            job.minute.on(0)  # Run at the top of every hour
            logger.info("Setting schedule: Hourly at minute 0")
        elif frequency == "daily":
            job.minute.on(0)
            job.hour.on(6)  # Run daily at 6 AM
            logger.info("Setting schedule: Daily at 6:00 AM")
        elif frequency == "custom":
            # Parse custom schedule from arguments
            parser = argparse.ArgumentParser(description="Schedule communication centralizer job")
            parser.add_argument("--minute", type=str, default="0", help="Cron minute specification")
            parser.add_argument("--hour", type=str, default="*", help="Cron hour specification")
            parser.add_argument("--day", type=str, default="*", help="Cron day specification")
            parser.add_argument("--month", type=str, default="*", help="Cron month specification")
            parser.add_argument("--weekday", type=str, default="*", help="Cron weekday specification")
            args = parser.parse_args(sys.argv[2:] if len(sys.argv) > 2 else [])

            job.setall(args.minute, args.hour, args.day, args.month, args.weekday)
            logger.info(
                f"Setting custom schedule: {args.minute} {args.hour} {args.day} {args.month} {args.weekday}"
            )
        else:
            logger.error(f"Unknown frequency: {frequency}")
            return False

        # Save the crontab
        cron.write()
        logger.info("Cron job scheduled successfully")
        return True

    except Exception as e:
        logger.error(f"Error scheduling job: {str(e)}", exc_info=True)
        return False


def remove_job() -> bool:
    """
    Remove the scheduled communication centralizer job.

    Returns:
        True if removed successfully, False otherwise
    """
    try:
        # Get current user crontab
        cron = CronTab(user=True)

        # Remove existing jobs for this script
        for job in cron.find_comment("communication-centralizer"):
            cron.remove(job)
            logger.info(f"Removed job: {job}")

        # Save the crontab
        cron.write()
        logger.info("Cron job removed successfully")
        return True

    except Exception as e:
        logger.error(f"Error removing job: {str(e)}", exc_info=True)
        return False


def display_job() -> bool:
    """
    Display the scheduled communication centralizer job.

    Returns:
        True if job exists, False otherwise
    """
    try:
        # Get current user crontab
        cron = CronTab(user=True)

        # Find jobs for this script
        jobs = list(cron.find_comment("communication-centralizer"))

        if not jobs:
            logger.info("No scheduled jobs found")
            return False

        # Display jobs
        for job in jobs:
            logger.info(f"Scheduled job: {job}")

        return True

    except Exception as e:
        logger.error(f"Error displaying job: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schedule or manage communication centralizer jobs")
    parser.add_argument(
        "action",
        choices=["schedule", "remove", "display"],
        help="Action to perform (schedule, remove, or display jobs)",
    )
    parser.add_argument(
        "--frequency",
        choices=["hourly", "daily", "custom"],
        default="hourly",
        help="Frequency for job scheduling (hourly, daily, custom)",
    )

    if len(sys.argv) > 1:
        args = parser.parse_args(sys.argv[1:2])  # Only parse the action argument

        if args.action == "schedule":
            if len(sys.argv) > 2:
                freq_args = parser.parse_args(sys.argv[1:3])
                schedule_job(freq_args.frequency)
            else:
                schedule_job()
        elif args.action == "remove":
            remove_job()
        elif args.action == "display":
            display_job()
    else:
        parser.print_help()
