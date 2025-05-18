class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def greet(self) -> str:
        """Return a greeting message.
        
        Returns
        -------
        str
            A greeting message including the person's name.
        """
        return f"Hello, my name is {self.name} and I am {self.age} years old."
    
    def have_birthday(self) -> None:
        """Increment the person's age by 1."""
        self.age += 1


# Example usage
def main() -> None:
    # Create a new person
    person = Person("Alice", 30)
    
    # Print greeting
    print(person.greet())
    
    # Celebrate birthday
    person.have_birthday()
    
    # Print greeting again
    print(person.greet())


if __name__ == "__main__":
    main()