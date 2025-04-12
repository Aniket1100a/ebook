import time

class SwitchForm:
    def __init__(self):
        # Representing the two forms as simple variables
        self.form_a = "Sign In Form"
        self.form_b = "Sign Up Form"
        self.switch_state = False  # False means form_a is visible, True means form_b is visible

    def toggle_forms(self):
        # This method simulates switching between two forms
        if self.switch_state:
            print(f"Switching to: {self.form_a}")
            self.switch_state = False
        else:
            print(f"Switching to: {self.form_b}")
            self.switch_state = True
        
        self.animate_switch()

    def animate_switch(self):
        # Simulate the animation delay (could represent transition time)
        print("Animating switch...")
        time.sleep(1.5)  # 1.5 second animation time
        print("Switch animation complete!")

    def submit_form(self):
        print("Form submitted.")

# Main function to simulate the form switch logic
def main():
    switch_form = SwitchForm()

    # Simulating user clicks on switch buttons
    while True:
        action = input("Press 's' to switch forms or 'q' to quit: ")
        if action.lower() == 's':
            switch_form.toggle_forms()
        elif action.lower() == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main()
