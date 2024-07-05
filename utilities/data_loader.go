package main

import (
    "encoding/csv"
    "fmt"
    "os"
)

func loadData(filePath string) ([][]string, error) {
    file, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    reader := csv.NewReader(file)
    data, err := reader.ReadAll()
    if err != nil {
        return nil, err
    }
    return data, nil
}

func main() {
    data, err := loadData("data.csv")
    if err != nil {
        panic(err)
    }
    for _, row := range data {
        fmt.Println(row)
    }
}
