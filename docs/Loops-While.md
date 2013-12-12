# while

`(while CONDITION EXPRESSION...)`

The macro `while` takes a condition and a variable number of
expressions. It evaluates the expressions if the condition evaluates
to a truthy value, then repeats until the condition evaluates to a
falsey value.

Always returns `null`.

Examples:

    > (do
        (set! i 1) ;; TODO: use let
        (set! total 0)
        (while (< i 11)
          (set! total (+ total i ))
        )
        total
    )
    
    
        
