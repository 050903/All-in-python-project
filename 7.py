import random

def play_game():
    """
    Manages a single round of the number guessing game.
    """
    # The computer selects a random number between 1 and 100.
    secret_number = random.randint(1, 100)
    attempts = 0
    guess = 0

    print("\nI'm thinking of a number between 1 and 100.")
    print("Can you guess what it is?")

    # Loop until the player guesses the correct number.
    while guess != secret_number:
        try:
            # Prompt the player for their guess.
            guess_input = input("Enter your guess: ")
            guess = int(guess_input)
            attempts += 1 # Increment the attempt counter after a valid input.

            # Compare the guess to the secret number and provide feedback.
            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                # The guess is correct.
                print(f"\nCorrect! You guessed it in {attempts} tries.")
                print("Congratulations!")

        except ValueError:
            # Handle cases where the input is not a valid number.
            print("Invalid input. Please enter a whole number.")

def main():
    """
    Main function to run the game and handle restarts.
    """
    print("--- Welcome to the Number Guessing Game! ---")

    while True:
        play_game() # Start a round of the game.

        # Ask the player if they want to play again.
        while True:
            play_again = input("\nPlay another round? (Y/N): ").lower()
            if play_again in ['y', 'n']:
                break
            print("Invalid input. Please enter 'Y' or 'N'.")

        if play_again == 'n':
            print("Thanks for playing!")
            break # Exit the main game loop.

# Entry point of the program.
if __name__ == "__main__":
    main()
