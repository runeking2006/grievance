import { apiClient } from "@/api/client";

export type ComplaintPayload = {
  text: string;
  location?: string;
};

export type ComplaintResponse = {
  complaint_id?: number | null;
  category: string;
  urgency: string;
  department: string;
  insight: string;
  status: string;
  deadline?: string | null;
  similar_complaints: string[];
  processing_status: string;
  owner_id?: string | null;
  escalated: boolean;
  escalation_level: number;
};

export type ComplaintJob = {
  job_id: number;
  grievance_id: number;
  status: string;
  job_type: string;
  error_message?: string | null;
};

export type OwnedComplaint = {
  complaint_id: number;
  complaint_text: string;
  category?: string | null;
  urgency?: string | null;
  department?: string | null;
  status: string;
  processing_status: string;
  escalated: boolean;
  escalation_level: number;
  created_at: string;
};

export async function submitComplaint(payload: ComplaintPayload): Promise<ComplaintResponse> {
  const { data } = await apiClient.post<ComplaintResponse>("/complaint", payload);
  return data;
}

export async function submitComplaintAsync(payload: ComplaintPayload): Promise<ComplaintJob> {
  const { data } = await apiClient.post<ComplaintJob>("/complaint/async", payload);
  return data;
}

export async function fetchJob(jobId: number): Promise<ComplaintJob> {
  const { data } = await apiClient.get<ComplaintJob>(`/jobs/${jobId}`);
  return data;
}

export async function fetchMyComplaints(): Promise<OwnedComplaint[]> {
  const { data } = await apiClient.get<OwnedComplaint[]>("/my-complaints");
  return data;
}
