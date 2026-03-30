"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

import {
  fetchJob,
  fetchMyComplaints,
  submitComplaint,
  submitComplaintAsync,
  type ComplaintPayload,
} from "@/api/complaint";
import { getStoredToken } from "@/store/authStore";
import { useUiStore } from "@/store/uiStore";
import { QUERY_KEYS, WS_BASE_URL } from "@/utils/constants";

export function useComplaint() {
  const queryClient = useQueryClient();
  const addToast = useUiStore((state) => state.addToast);

  const complaintMutation = useMutation({
    mutationFn: (payload: ComplaintPayload) => submitComplaint(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.myComplaints });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.stats });
      addToast({
        title: "Complaint submitted",
        description: "AI triage completed successfully.",
        tone: "success",
      });
    },
    onError: (error) => {
      if (axios.isAxiosError(error)) {
        addToast({
          title: "Submission failed",
          description: error.response?.data?.detail ?? error.message,
          tone: "error",
        });
      }
    },
  });

  const asyncComplaintMutation = useMutation({
    mutationFn: (payload: ComplaintPayload) => submitComplaintAsync(payload),
    onSuccess: (job) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.myComplaints });
      addToast({
        title: "Complaint queued",
        description: `Background job #${job.job_id} is processing.`,
        tone: "success",
      });
    },
    onError: (error) => {
      if (axios.isAxiosError(error)) {
        addToast({
          title: "Async submission failed",
          description: error.response?.data?.detail ?? error.message,
          tone: "error",
        });
      }
    },
  });

  return { complaintMutation, asyncComplaintMutation };
}

export function useJobStatus(jobId: number | null) {
  const [socketJob, setSocketJob] = useState<{ jobId: number; data: Awaited<ReturnType<typeof fetchJob>> } | null>(null);
  const [socketReadyJobId, setSocketReadyJobId] = useState<number | null>(null);
  const token = getStoredToken();

  useEffect(() => {
    if (jobId === null || !token) {
      return;
    }

    let active = true;
    const socket = new WebSocket(`${WS_BASE_URL}/ws/jobs/${jobId}?token=${encodeURIComponent(token)}`);

    socket.onopen = () => {
      if (active) {
        setSocketReadyJobId(jobId);
      }
    };

    socket.onmessage = (event) => {
      if (!active) {
        return;
      }
      try {
        setSocketJob({ jobId, data: JSON.parse(event.data) });
      } catch {
        setSocketReadyJobId(null);
      }
    };

    socket.onerror = () => {
      if (active) {
        setSocketReadyJobId(null);
      }
    };

    socket.onclose = () => {
      if (active) {
        setSocketReadyJobId(null);
      }
    };

    return () => {
      active = false;
      socket.close();
    };
  }, [jobId, token]);

  const pollQuery = useQuery({
    queryKey: QUERY_KEYS.job(jobId),
    queryFn: () => fetchJob(jobId as number),
    enabled: jobId !== null,
    refetchInterval: (query) => {
      if (socketReadyJobId === jobId) {
        return false;
      }
      const status = query.state.data?.status;
      return status === "queued" || status === "processing" ? 2500 : false;
    },
  });

  return {
    ...pollQuery,
    data: socketJob?.jobId === jobId ? socketJob.data : pollQuery.data,
    isLive: socketReadyJobId === jobId,
  };
}

export function useMyComplaints() {
  return useQuery({
    queryKey: QUERY_KEYS.myComplaints,
    queryFn: fetchMyComplaints,
  });
}
