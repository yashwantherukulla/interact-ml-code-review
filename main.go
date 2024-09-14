package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
)

type AnalysisRequest struct {
	RepoLinks []string `json:"repo_links"`
}

type AnalysisResponse struct {
	Message string `json:"message"`
	Error   string `json:"error,omitempty"`
}

func analyzeRepoHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AnalysisRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.RepoLinks == nil {
		http.Error(w, "Repository link is required", http.StatusBadRequest)
		return
	}
	
	linkArgs := fmt.Sprintf("%v", req.RepoLinks)
	cmd := exec.Command("bash", "run_analysis.sh", linkArgs)
	output, err := cmd.CombinedOutput()

	resp := AnalysisResponse{}

	if err != nil {
		resp.Error = fmt.Sprintf("Error executing Python script: %v", err)
		resp.Message = string(output)
	} else {
		resp.Message = fmt.Sprintf("Repository analysis completed successfully. Output: %s", string(output))
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/analyze-repo", analyzeRepoHandler)
	
	fmt.Println("Server is running on localhost:8080")
	log.Fatal(http.ListenAndServe("localhost:8080", nil))
}