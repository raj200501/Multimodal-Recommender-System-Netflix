package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "os"
)

type Config struct {
    DatabaseURL  string `json:"database_url"`
    ApiKey       string `json:"api_key"`
    MaxRetries   int    `json:"max_retries"`
}

func loadConfig(filePath string) (Config, error) {
    var config Config
    file, err := os.Open(filePath)
    if err != nil {
        return config, err
    }
    defer file.Close()

    bytes, err := ioutil.ReadAll(file)
    if err != nil {
        return config, err
    }

    err = json.Unmarshal(bytes, &config)
    return config, err
}

func main() {
    config, err := loadConfig("config.json")
    if err != nil {
        panic(err)
    }
    fmt.Printf("Config: %+v\n", config)
}
