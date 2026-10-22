import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {

    if (page === "dashboard") {

      axios
        .get("http://127.0.0.1:8000/dashboard")
        .then((response) => {
          setDashboard(response.data);
        })
        .catch((error) => {
          console.error("Dashboard error:", error);
        });

    }

  }, [page]);

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF or DOCX file.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData
      );

      setResult(response.data);
    } catch (err) {
      setError("Unable to analyze the document.");
    }

    setLoading(false);
  };

  return (
    <div className="app">

      {/* Header */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            SD
          </div>

          <div>
            <h1>
              Smart Document Compliance
            </h1>

            <p>
              Contract Intelligence & Risk Analysis
            </p>
          </div>

        </div>


        <nav className="navigation">

          <button
            className={
              page === "dashboard"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => setPage("dashboard")}
          >
            Dashboard
          </button>


          <button
            className={
              page === "analyzer"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => setPage("analyzer")}
          >
            Contract Analyzer
          </button>

        </nav>

      </header>


      <main className="container">

        {page === "dashboard" && dashboard && (

          <section className="dashboard">

            <div className="dashboard-heading">

              <div>

                <span className="eyebrow">
                  AUTOMATION OVERVIEW
                </span>

                <h2>
                  Processing Dashboard
                </h2>

                <p>
                  Monitor contracts processed by the
                  document compliance automation.
                </p>

              </div>

              <div className="bot-status">
                <span className="status-dot"></span>
                Automation Bot Active
              </div>

            </div>


            {/* Statistics */}

            <div className="dashboard-stats">

              <div className="dashboard-stat">

                <span>
                  TOTAL PROCESSED
                </span>

                <strong>
                  {dashboard.total_processed}
                </strong>

              </div>


              <div className="dashboard-stat">

                <span>
                  LOW RISK
                </span>

                <strong>
                  {dashboard.low_risk}
                </strong>

              </div>


              <div className="dashboard-stat">

                <span>
                  MEDIUM RISK
                </span>

                <strong>
                  {dashboard.medium_risk}
                </strong>

              </div>


              <div className="dashboard-stat">

                <span>
                  HIGH RISK
                </span>

                <strong>
                  {dashboard.high_risk}
                </strong>

              </div>

            </div>


            {/* Processing History */}

            <div className="content-card">

              <div className="card-heading">

                <h3>
                  Processing History
                </h3>

                <p>
                  Contracts processed by the automation workflow
                </p>

              </div>


              {dashboard.records.length === 0 ? (

                <div className="empty-state">

                  <div>
                    📄
                  </div>

                  <strong>
                    No contracts processed yet
                  </strong>

                  <p>
                    Place a contract inside the incoming
                    folder to start the automation.
                  </p>

                </div>

              ) : (

                <div className="table-container">

                  <table>

                    <thead>

                      <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Contract</th>
                        <th>Score</th>
                        <th>Risk</th>
                        <th>Status</th>
                      </tr>

                    </thead>


                    <tbody>

                      {[...dashboard.records]
                        .reverse()
                        .map((record, index) => (

                          <tr key={index}>

                            <td>
                              {record.Date}
                            </td>

                            <td>
                              {record.Time}
                            </td>

                            <td className="contract-name">
                              {record.Contract}
                            </td>

                            <td>
                              {record["Compliance Score"]
                                ? `${record["Compliance Score"]}%`
                                : "-"}
                            </td>

                            <td>

                              <span
                                className={`risk-badge ${record[
                                  "Risk Level"
                                ].toLowerCase()}`}
                              >
                                {record["Risk Level"]}
                              </span>

                            </td>

                            <td>

                              <span className="completed">
                                ✓ {record.Status}
                              </span>

                            </td>

                          </tr>

                        ))}

                    </tbody>

                  </table>

                </div>

              )}

            </div>

          </section>

        )}

        {/* Upload Section */}

        {page === "analyzer" && !result && (
          <section className="upload-section">

            <div className="section-heading">
              <span className="eyebrow">
                DOCUMENT ANALYSIS
              </span>

              <h2>
                Analyze your contract
              </h2>

              <p>
                Upload a PDF or DOCX contract to detect
                important clauses and evaluate compliance.
              </p>
            </div>


            <div className="upload-card">

              <div className="upload-icon">
                📄
              </div>

              <h3>
                Upload Contract
              </h3>

              <p>
                Supported formats: PDF and DOCX
              </p>

              <input
                id="file-upload"
                type="file"
                accept=".pdf,.docx"
                onChange={(e) =>
                  setFile(e.target.files[0])
                }
              />

              <label
                htmlFor="file-upload"
                className="choose-button"
              >
                Choose Document
              </label>


              {file && (
                <div className="selected-file">
                  <span>📎</span>

                  <div>
                    <strong>{file.name}</strong>
                    <small>Ready for analysis</small>
                  </div>
                </div>
              )}


              <button
                className="analyze-button"
                onClick={handleUpload}
                disabled={loading}
              >
                {loading
                  ? "Analyzing Contract..."
                  : "Analyze Contract"}
              </button>

            </div>

            {error && (
              <div className="error">
                {error}
              </div>
            )}

          </section>
        )}


        {/* Results */}

        {page === "analyzer" && result && !result.error && (

          <section className="results-section">

            <div className="results-header">

              <div>
                <span className="eyebrow">
                  ANALYSIS COMPLETE
                </span>

                <h2>
                  Contract Analysis
                </h2>

                <p className="document-name">
                  📄 {result.filename}
                </p>
              </div>

              <button
                className="new-analysis"
                onClick={() => {
                  setResult(null);
                  setFile(null);
                }}
              >
                + New Analysis
              </button>

            </div>


            {/* Summary Cards */}

            <div className="summary-grid">

              <div className="summary-card score-card">

                <span>
                  COMPLIANCE SCORE
                </span>

                <strong>
                  {result.compliance_score}%
                </strong>

                <small>
                  Overall compliance
                </small>

              </div>


              <div className="summary-card">

                <span>
                  RISK LEVEL
                </span>

                <strong>
                  {result.risk_level}
                </strong>

                <small>
                  Based on detected clauses
                </small>

              </div>


              <div className="summary-card">

                <span>
                  MISSING CLAUSES
                </span>

                <strong>
                  {result.missing_clauses.length}
                </strong>

                <small>
                  Clauses requiring attention
                </small>

              </div>

            </div>


            {/* Clause Analysis */}

            <div className="content-card">

              <div className="card-heading">

                <div>
                  <h3>Clause Analysis</h3>

                  <p>
                    Detected clauses and supporting evidence
                  </p>
                </div>

              </div>


              <div className="clause-list">

                {Object.entries(result.clauses).map(
                  ([clause, data]) => (

                    <div
                      className={`clause-item ${data.found
                        ? "clause-found"
                        : "clause-missing"
                        }`}
                      key={clause}
                    >

                      <div className="clause-top">

                        <div className="clause-title">

                          <span className="status-icon">
                            {data.found ? "✓" : "!"}
                          </span>

                          <strong>
                            {clause}
                          </strong>

                        </div>


                        <span
                          className={`strength ${data.found
                            ? data.match_strength.toLowerCase()
                            : "none"
                            }`}
                        >
                          {data.found
                            ? data.match_strength
                            : "Missing"}
                        </span>

                      </div>


                      {data.found ? (

                        <>

                          <p className="evidence-label">
                            Supporting Evidence
                          </p>

                          <p className="evidence-text">
                            "{data.evidence}"
                          </p>

                          <p className="detected-terms">
                            Detected terms:{" "}
                            {data.matched_keywords.join(", ")}
                          </p>

                        </>

                      ) : (

                        <p className="missing-text">
                          No relevant clause was detected
                          in this document.
                        </p>

                      )}

                    </div>

                  )
                )}

              </div>

            </div>


            {/* Recommendations */}

            {result.missing_clauses.length > 0 && (

              <div className="content-card recommendations-card">

                <div className="card-heading">

                  <div>
                    <h3>
                      ⚠ Recommendations
                    </h3>

                    <p>
                      Areas that may require attention
                    </p>
                  </div>

                </div>


                {result.missing_clauses.map(
                  (clause) => (

                    <div
                      className="recommendation"
                      key={clause}
                    >

                      <strong>
                        {clause}
                      </strong>

                      <p>
                        {result.recommendations[clause]}
                      </p>

                    </div>

                  )
                )}

              </div>

            )}


            {/* Download */}

            <div className="report-section">

              <a
                className="download-button"
                href={`http://127.0.0.1:8000/report/${result.report}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Download Compliance Report
              </a>

            </div>

          </section>

        )}

      </main>

    </div>
  );
}

export default App;