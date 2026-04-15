package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/mux"
)

// BuildInfo contains version and build metadata
type BuildInfo struct {
	Version   string `json:"version"`
	GoVersion string `json:"go_version"`
	BuildTime string `json:"build_time"`
}

// ServiceInfo contains runtime service information
type ServiceInfo struct {
	Uptime   string `json:"uptime"`
	Hostname string `json:"hostname"`
}

// APIResponse is a standard JSON response wrapper
type APIResponse struct {
	Status  string      `json:"status"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
}

// buildInfo holds the compiled build information
var buildInfo = BuildInfo{
	Version:   "1.0.0",
	GoVersion: "1.21",
	BuildTime: time.Now().Format(time.RFC3339),
}

// startTime is used to calculate uptime
var startTime = time.Now()

// healthHandler handles GET /health
func healthHandler(w http.ResponseWriter, r *http.Request) {
	// Check database connectivity and other dependencies here if needed
	healthy := true
	status := "healthy"

	if !healthy {
		status = "unhealthy"
		w.WriteHeader(http.StatusServiceUnavailable)
	}

	response := APIResponse{
		Status:  status,
		Message: "Service is operational",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// infoHandler handles GET /info
func infoHandler(w http.ResponseWriter, r *http.Request) {
	uptime := time.Since(startTime).Truncate(time.Second).String()

	serviceInfo := ServiceInfo{
		Uptime:   uptime,
		Hostname: r.Host,
	}

	response := APIResponse{
		Status: "ok",
		Data: map[string]interface{}{
			"build":  buildInfo,
			"service": serviceInfo,
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	router := mux.NewRouter()

	// Health check endpoint
	router.HandleFunc("/health", healthHandler).Methods("GET")

	// Service info endpoint
	router.HandleFunc("/info", infoHandler).Methods("GET")

	log.Println("Server starting on :8080")
	log.Fatal(http.ListenAndServe(":8080", router))
}