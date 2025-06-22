import random
import string
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

def generate_password(length, use_uppercase, use_lowercase, use_digits, use_special):
    """Generates a random password based on user-defined criteria."""
    
    character_pool = ''
    if use_uppercase:
        character_pool += string.ascii_uppercase
    if use_lowercase:
        character_pool += string.ascii_lowercase
    if use_digits:
        character_pool += string.digits
    if use_special:
        character_pool += string.punctuation

    if not character_pool:
        return None  # Should not happen with validation, but as a safeguard

    password_list = random.choices(character_pool, k=length)
    password = ''.join(password_list)
    return password

def main():
    """Main function to run the password generator app."""
    
    print("Welcome to the Password Generator!")

    # Get password length
    while True:
        try:
            length = int(input("Enter the desired password length (e.g., 12): "))
            if length > 0:
                break
            else:
                print("Password length must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get character type preferences from a single input
    use_uppercase = use_lowercase = use_digits = use_special = False
    while True:
        prompt = (
            "Which character types to include? (enter any combination of u, l, d, s)\n"
            "  u = uppercase (A-Z)\n"
            "  l = lowercase (a-z)\n"
            "  d = digits (0-9)\n"
            "  s = special characters (!@#$)\n"
            "Your choice(s) (e.g., 'uld'): "
        )
        choices = input(prompt).lower()

        if choices and all(c in 'ulds' for c in choices):
            use_uppercase = 'u' in choices
            use_lowercase = 'l' in choices
            use_digits = 'd' in choices
            use_special = 's' in choices
            break
        else:
            print("Invalid input. Please enter a valid combination of 'u', 'l', 'd', 's'.")

    # Get number of passwords to generate
    while True:
        try:
            num_input = input("How many passwords would you like to generate? (Default: 1): ")
            if num_input == "":
                num_passwords = 1
                break
            num_passwords = int(num_input)
            if num_passwords > 0:
                break
            else:
                print("Please enter a number greater than 0.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Generate and display the passwords
    print(f"\nGenerating {num_passwords} password(s):")
    generated_passwords = []
    for i in range(num_passwords):
        password = generate_password(length, use_uppercase, use_lowercase, use_digits, use_special)
        if password:
            generated_passwords.append(password)
            print(f"  {i + 1}: {password}")

    # Copy to clipboard feature
    if PYPERCLIP_AVAILABLE and generated_passwords:
        while True:
            copy_choice = input("\nCopy a password to clipboard? (Y/N): ").lower()
            if copy_choice in ['y', 'n']:
                break
            print("Invalid input. Please enter 'Y' or 'N'.")

        if copy_choice == 'y':
            while True:
                try:
                    pw_num_str = input(f"Enter the password number to copy (1-{len(generated_passwords)}): ")
                    pw_num = int(pw_num_str)
                    if 1 <= pw_num <= len(generated_passwords):
                        password_to_copy = generated_passwords[pw_num - 1]
                        pyperclip.copy(password_to_copy)
                        print(f"Password #{pw_num} copied to clipboard.")
                        break
                    else:
                        print(f"Invalid number. Please enter a number between 1 and {len(generated_passwords)}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
    
    if not PYPERCLIP_AVAILABLE:
        print("\nNote: To enable the copy-to-clipboard feature, install the 'pyperclip' module:")
        print("pip install pyperclip")

if __name__ == "__main__":
    main()
