"""Main entry point for Portfolio Tracker CLI"""

from controller import PortfolioController
from view import PortfolioView


def main():
    """Main CLI loop"""
    view = PortfolioView()
    controller = PortfolioController(view)

    view.show_welcome() # Shows first output of the app, suggests typing help for more information
    
    while True:
        try:
            # Get user input
            user_input = view.get_user_input()
            
            # Parse command
            command, args = controller.parse_command(user_input)
            
            if command is None:
                continue  # Empty input
            
            # Execute command
            result = controller.execute_command(command, args)
            
            # Check if user wants to quit
            if result.upper() == "QUIT":
                view.show_goodbye()
                break

            # Display result (errors and simple confirmations)
            if result:
                view.display_message(result)
        
        except KeyboardInterrupt:
            print("\n")
            view.show_goodbye()
            break
        
        except Exception as e:
            view.display_error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
