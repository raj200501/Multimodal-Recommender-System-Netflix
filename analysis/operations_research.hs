module Main where

import Data.List

-- Example data and operations research logic
operationsResearch :: [Double] -> [Double] -> Double
operationsResearch x y = optimize x y

optimize :: [Double] -> [Double] -> Double
optimize x y = sum $ zipWith (*) x y

main :: IO ()
main = do
    let x = [1.0, 2.0, 3.0, 4.0, 5.0]
    let y = [2.0, 4.0, 6.0, 8.0, 10.0]
    let result = operationsResearch x y
    print result
