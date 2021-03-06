#include "turingarena.h"

#include <cstdlib>
#include <ctime>
#include <iostream>

int main() 
{
    srand(time(nullptr));

    int correct = rand() % 100;
    int number_of_guesses = 0;

    auto guess = [&number_of_guesses, correct](int n) {
        number_of_guesses++;
        if (n == correct) 
            return 0; // ok
        if (n < correct)
            return -1; // too low
        if (n > correct)
            return 1; // to high
    };

    int ans;
    {
        turingarena::Algorithm algorithm{turingarena::submission["source"]};
        ans = algorithm.call_function("play", std::make_tuple(guess), correct);
    }

    if (ans == correct)
        std::cout << "CORRECT in " << number_of_guesses << " guesses\n";
    else 
        std::cout << "WRONG\n";
}