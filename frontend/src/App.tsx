import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { ReportPage } from './pages/ReportPage';
import { EvidenceAnalysisPage } from './pages/EvidenceAnalysisPage';
import { TrackingPage } from './pages/TrackingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ReportsListPage } from './pages/ReportsListPage';
import { ShieldCheck, Heart } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'report' | 'dashboard' | 'track' | 'list'>('report');
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [trackingReportId, setTrackingReportId] = useState<string | null>(null);

  const handleReportCreated = (reportId: string) => {
    setSelectedReportId(reportId);
    // Switch to analysis view
  };

  const handleSelectReport = (reportId: string) => {
    setSelectedReportId(reportId);
  };

  const handleNavigateTrack = (reportId: string) => {
    setTrackingReportId(reportId);
    setSelectedReportId(null);
    setActiveTab('track');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setSelectedReportId(null);
        }}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {selectedReportId ? (
          <EvidenceAnalysisPage
            reportId={selectedReportId}
            onBack={() => setSelectedReportId(null)}
            onNavigateTrack={handleNavigateTrack}
          />
        ) : (
          <>
            {activeTab === 'report' && <ReportPage onReportCreated={handleReportCreated} />}
            {activeTab === 'dashboard' && <DashboardPage onSelectReport={handleSelectReport} />}
            {activeTab === 'track' && (
              <TrackingPage
                initialReportId={trackingReportId}
                onNavigateAnalyze={handleSelectReport}
              />
            )}
            {activeTab === 'list' && <ReportsListPage onSelectReport={handleSelectReport} />}
          </>
        )}
      </main>

      {/* Ethical Civic Tech Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span className="font-semibold text-slate-700">CivicPulse AI</span>
            <span>—</span>
            <span>Local Multimodal Inference via Qwen2.5-VL & Qwen2.5</span>
          </div>

          <div className="text-center sm:text-right text-[11px] text-slate-500">
            <strong>Core Principle:</strong> AI extracts evidence; deterministic Python rules recommend actions; authorized humans handle consequential decisions.
          </div>
        </div>
      </footer>
    </div>
  );
}
