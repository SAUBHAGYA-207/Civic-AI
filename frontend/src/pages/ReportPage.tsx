import React, { useState } from 'react';
import { UploadCloud, MapPin, X, ArrowRight, CheckCircle2, AlertCircle, Loader2, Sparkles, Navigation } from 'lucide-react';
import { createReport } from '../api/client';
import { IssueCategory } from '../types';

interface ReportPageProps {
  onReportCreated: (reportId: string) => void;
}

export const ReportPage: React.FC<ReportPageProps> = ({ onReportCreated }) => {
  const [complaintText, setComplaintText] = useState('');
  const [addressOrLandmark, setAddressOrLandmark] = useState('');
  const [category, setCategory] = useState<IssueCategory>('unknown');
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<{ id: string; message: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const files = Array.from(e.target.files);
    
    // Check sizes & extensions
    const validFiles: File[] = [];
    const validPreviews: string[] = [];

    files.forEach((file) => {
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} exceeds 10MB limit.`);
        return;
      }
      validFiles.push(file);
      validPreviews.push(URL.createObjectURL(file));
    });

    setSelectedFiles((prev) => [...prev, ...validFiles]);
    setPreviews((prev) => [...prev, ...validPreviews]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    setPreviews((prev) => prev.filter((_, i) => i !== index));
  };

  const requestGeolocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(parseFloat(position.coords.latitude.toFixed(6)));
        setLongitude(parseFloat(position.coords.longitude.toFixed(6)));
        setGeoLoading(false);
      },
      (error) => {
        setGeoLoading(false);
        alert(`Location permission error: ${error.message}`);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintText.trim()) {
      setErrorMessage('Please provide a description of the civic problem.');
      return;
    }
    setErrorMessage(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('complaint_text', complaintText.trim());
      if (addressOrLandmark.trim()) {
        formData.append('address_or_landmark', addressOrLandmark.trim());
      }
      if (category && category !== 'unknown') {
        formData.append('citizen_category', category);
      }
      if (latitude !== null) formData.append('latitude', latitude.toString());
      if (longitude !== null) formData.append('longitude', longitude.toString());

      selectedFiles.forEach((file) => {
        formData.append('images', file);
      });

      const res = await createReport(formData);
      setSuccessData({ id: res.report_id, message: res.message });
      setLoading(false);
    } catch (err: any) {
      setErrorMessage(err.message || 'Submission failed');
      setLoading(false);
    }
  };

  if (successData) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Grievance Registered Successfully</h2>
          <p className="text-slate-600 mb-6">
            Your complaint has been securely recorded on the local civic ledger.
          </p>

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 inline-block text-left w-full">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Assigned Grievance ID</div>
            <div className="text-sm sm:text-base font-mono font-bold text-blue-700 select-all break-all">{successData.id}</div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => onReportCreated(successData.id)}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold transition shadow-md shadow-blue-500/20"
            >
              <Sparkles className="w-4 h-4" />
              <span>Inspect AI Evidence Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setSuccessData(null);
                setComplaintText('');
                setAddressOrLandmark('');
                setSelectedFiles([]);
                setPreviews([]);
                setLatitude(null);
                setLongitude(null);
              }}
              className="px-6 py-3 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold transition"
            >
              Submit Another Report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Report Civic Grievance</h1>
        <p className="text-slate-600 mt-2 text-sm sm:text-base">
          Submit photographs and details regarding damaged roads, water leaks, open drains, or uncollected waste.
          Local AI models extract evidence transparently without sending your data to external corporate cloud APIs.
        </p>
      </div>

      {errorMessage && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-600" />
          <div>{errorMessage}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8 space-y-6">
        {/* Photo Upload Area */}
        <div>
          <label className="block text-sm font-bold text-slate-900 mb-1">
            Photographs of the Issue <span className="text-slate-400 font-normal">(Optional but recommended)</span>
          </label>
          <p className="text-xs text-slate-500 mb-3">
            Clear photographs allow Qwen2.5-VL to isolate visible physical observations.
          </p>

          <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-blue-500 transition cursor-pointer relative bg-slate-50/50">
            <input
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center justify-center">
              <UploadCloud className="w-10 h-10 text-slate-400 mb-2" />
              <p className="text-sm font-semibold text-slate-700">Click or drag photos to upload</p>
              <p className="text-xs text-slate-500 mt-1">JPEG, PNG, or WebP up to 10MB each</p>
            </div>
          </div>

          {/* Previews */}
          {previews.length > 0 && (
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
              {previews.map((url, idx) => (
                <div key={idx} className="relative rounded-lg overflow-hidden border border-slate-200 aspect-video group bg-slate-100">
                  <img src={url} alt={`Preview ${idx + 1}`} className="w-full h-full object-cover" />
                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    className="absolute top-1 right-1 p-1 rounded-full bg-slate-900/70 text-white hover:bg-rose-600 transition"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Complaint Text */}
        <div>
          <label className="block text-sm font-bold text-slate-900 mb-1">
            Complaint Description <span className="text-rose-600">*</span>
          </label>
          <textarea
            required
            rows={4}
            value={complaintText}
            onChange={(e) => setComplaintText(e.target.value)}
            placeholder="Describe what is broken, for how long it has been occurring, and any immediate hazards or traffic blockages..."
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm placeholder:text-slate-400"
          />
          <div className="flex justify-between items-center text-xs text-slate-400 mt-1">
            <span>Minimum 5 characters</span>
            <span>{complaintText.length} / 4000</span>
          </div>
        </div>

        {/* Location Section */}
        <div className="space-y-3">
          <label className="block text-sm font-bold text-slate-900 mb-1">
            Location Information
          </label>
          <div>
            <input
              type="text"
              value={addressOrLandmark}
              onChange={(e) => setAddressOrLandmark(e.target.value)}
              placeholder="Address, road name, nearby landmark, or ward number"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={requestGeolocation}
              disabled={geoLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition"
            >
              {geoLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" /> : <Navigation className="w-3.5 h-3.5 text-blue-600" />}
              <span>{latitude && longitude ? 'Update Device GPS' : 'Attach Device GPS Coordinates'}</span>
            </button>

            {latitude && longitude && (
              <span className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-md flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                Lat: {latitude}, Lon: {longitude}
              </span>
            )}
          </div>
        </div>

        {/* Category Hint */}
        <div>
          <label className="block text-sm font-bold text-slate-900 mb-1">
            Citizen Issue Category Hint <span className="text-slate-400 font-normal">(Optional)</span>
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as IssueCategory)}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white"
          >
            <option value="unknown">Unsure / Let AI & Reviewer Classify</option>
            <option value="road_damage">Road Damage (Potholes, cracks, asphalt breakdown)</option>
            <option value="water_leakage">Water Leakage (Broken main pipeline, leaking valve)</option>
            <option value="drainage">Drainage & Sewerage (Overflowing drain, open manhole)</option>
            <option value="waste_management">Municipal Waste (Uncollected garbage, open dump)</option>
            <option value="streetlight">Streetlight & Electrical (Dark lamp post, hanging wire)</option>
            <option value="other">Other Infrastructure Issue</option>
          </select>
          <p className="text-[11px] text-slate-400 mt-1">
            Note: Your selection is treated as an advisory hint. AI extracts physical evidence, and deterministic rules corroborate it.
          </p>
        </div>

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold transition shadow-md shadow-blue-500/20 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Registering Grievance...</span>
              </>
            ) : (
              <>
                <span>Submit Grievance</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
