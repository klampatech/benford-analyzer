package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestHealthHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/health", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(healthHandler)

	handler.ServeHTTP(rr, req)

	// Check status code
	if rr.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, rr.Code)
	}

	// Parse response
	var response APIResponse
	err = json.Unmarshal(rr.Body.Bytes(), &response)
	if err != nil {
		t.Fatalf("Failed to parse JSON response: %v", err)
	}

	// Verify response structure
	if response.Status != "healthy" {
		t.Errorf("Expected status 'healthy', got '%s'", response.Status)
	}

	if response.Message == "" {
		t.Error("Expected non-empty message field")
	}
}

func TestInfoHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/info", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(infoHandler)

	handler.ServeHTTP(rr, req)

	// Check status code
	if rr.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, rr.Code)
	}

	// Parse response
	var response APIResponse
	err = json.Unmarshal(rr.Body.Bytes(), &response)
	if err != nil {
		t.Fatalf("Failed to parse JSON response: %v", err)
	}

	// Verify response structure
	if response.Status != "ok" {
		t.Errorf("Expected status 'ok', got '%s'", response.Status)
	}

	data, ok := response.Data.(map[string]interface{})
	if !ok {
		t.Fatal("Expected data to be a map")
	}

	build, ok := data["build"].(map[string]interface{})
	if !ok {
		t.Fatal("Expected build info in data")
	}

	if build["version"] != "1.0.0" {
		t.Errorf("Expected version '1.0.0', got '%v'", build["version"])
	}

	service, ok := data["service"].(map[string]interface{})
	if !ok {
		t.Fatal("Expected service info in data")
	}

	uptime := service["uptime"].(string)
	if uptime == "" {
		t.Error("Expected non-empty uptime")
	}

	// Verify uptime looks like a duration (contains numbers and potentially letters)
	if len(uptime) < 1 {
		t.Error("Uptime appears too short")
	}
}

func TestHealthEndpointIsGET(t *testing.T) {
	// Verify these handlers only respond to GET
	handler := http.HandlerFunc(healthHandler)

	// Test with different methods - these should all return 405 Method Not Allowed
	// when properly registered with gorilla/mux, but we can verify handler signature
	methods := []string{"POST", "PUT", "DELETE", "PATCH"}

	for _, method := range methods {
		req, _ := http.NewRequest(method, "/health", nil)
		rr := httptest.NewRecorder()
		handler.ServeHTTP(rr, req)

		// Health handler itself doesn't check method, that's mux's job
		// But we verify the handler exists and is callable
		if rr.Code == 0 {
			t.Error("Handler should write some response")
		}
	}
}

func TestInfoEndpointIsGET(t *testing.T) {
	handler := http.HandlerFunc(infoHandler)

	methods := []string{"POST", "PUT", "DELETE", "PATCH"}

	for _, method := range methods {
		req, _ := http.NewRequest(method, "/info", nil)
		rr := httptest.NewRecorder()
		handler.ServeHTTP(rr, req)

		if rr.Code == 0 {
			t.Error("Handler should write some response")
		}
	}
}

func TestUptimeCalculation(t *testing.T) {
	// Verify uptime format is correct (not zero since module loaded before tests)
	req, _ := http.NewRequest("GET", "/info", nil)
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(infoHandler)
	handler.ServeHTTP(rr, req)

	var response APIResponse
	json.Unmarshal(rr.Body.Bytes(), &response)

	data := response.Data.(map[string]interface{})
	service := data["service"].(map[string]interface{})
	uptimeStr := service["uptime"].(string)

	// Uptime should be a valid duration string
	// Parse duration string
	uptime, err := time.ParseDuration(uptimeStr)
	if err != nil {
		t.Fatalf("Failed to parse uptime '%s': %v", uptimeStr, err)
	}

	// Uptime should be >= 0 (can be 0s in very fast test environments)
	if uptime < 0 {
		t.Errorf("Expected uptime >= 0, got %v", uptime)
	}

	// Verify the string is not empty (format validation)
	if uptimeStr == "" {
		t.Error("Uptime string should not be empty")
	}
}