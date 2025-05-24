// Factorial calculation example
// Demonstrates function declarations, loops, conditionals, and arithmetic

int factorial(int n) {
    // Base case
    if (n <= 1) {
        return 1;
    }
    
    // Recursive case
    return n * factorial(n - 1);
}

int main() {
    int number = 5;
    int result;
    
    // Calculate factorial
    result = factorial(number);
    
    // Print result
    print("Factorial of ");
    print(number);
    print(" is ");
    print(result);
    
    return 0;
} 