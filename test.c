int main() {
    int x = 5;
    int y = 10;
    
    // Test arithmetic
    int z = x + y * 2;
    
    // Test if-else
    if (z > 20) {
        print("z is greater than 20");
        x = x + 1;
    } else {
        print("z is 20 or less");
        y = y - 1;
    }
    
    // Test while loop
    while (x < y) {
        x = x + 1;
        print(x);
    }
    
    return z;
}
