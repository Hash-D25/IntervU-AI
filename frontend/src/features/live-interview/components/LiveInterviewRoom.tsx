"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CandidateTile } from "@/features/live-interview/components/CandidateTile";
import { CaptionsPanel } from "@/features/live-interview/components/CaptionsPanel";
import { ControlBar } from "@/features/live-interview/components/ControlBar";
import { InterviewerTile } from "@/features/live-interview/components/InterviewerTile";
import { PreJoinScreen } from "@/features/live-interview/components/PreJoinScreen";
import { RoomTopBar } from "@/features/live-interview/components/RoomTopBar";
import { useCamera } from "@/features/live-interview/hooks/useCamera";
import { useElapsedTimer } from "@/features/live-interview/hooks/useElapsedTimer";
import { useMediaDevices } from "@/features/live-interview/hooks/useMediaDevices";
import { useMockLiveSession } from "@/features/live-interview/hooks/useMockLiveSession";
import { MOCK_PHASE } from "@/features/live-interview/mocks";
import type { RoomHeaderInfo } from "@/features/live-interview/types";
import { useMicrophone } from "@/features/voice/hooks/useMicrophone";

type LiveInterviewRoomProps = {
  interviewId: string;
  header: RoomHeaderInfo;
};

export function LiveInterviewRoom({ interviewId, header }: LiveInterviewRoomProps) {
  const router = useRouter();

  const camera = useCamera();
  const microphone = useMicrophone();
  const { cameras, microphones, refresh } = useMediaDevices();

  const [hasJoined, setHasJoined] = useState(false);
  const [cameraOn, setCameraOn] = useState(true);
  const [micOn, setMicOn] = useState(true);
  const [captionsOpen, setCaptionsOpen] = useState(true);
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [selectedMicrophoneId, setSelectedMicrophoneId] = useState<string | null>(null);

  const elapsedSeconds = useElapsedTimer(hasJoined);
  const { connectionStatus, turnState, isInterviewerSpeaking, captions } = useMockLiveSession({
    active: hasJoined,
    captionsEnabled: captionsOpen,
  });

  // Request camera + mic up front so the pre-join green room shows a preview,
  // and release both devices when the room unmounts (back nav, auth change, etc.).
  useEffect(() => {
    void camera.start();
    void microphone.startRecording();
    return () => {
      camera.stop();
      microphone.reset();
    };
    // Only run once on mount; hook identities are stable.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Populate device labels once permissions are granted.
  useEffect(() => {
    if (camera.state === "active" || microphone.state === "recording") {
      void refresh();
    }
  }, [camera.state, microphone.state, refresh]);

  // Track the active camera device for the picker.
  useEffect(() => {
    if (!camera.stream) {
      return;
    }
    const trackDeviceId = camera.stream.getVideoTracks()[0]?.getSettings().deviceId;
    if (trackDeviceId) {
      setSelectedCameraId(trackDeviceId);
    }
  }, [camera.stream]);

  // Default the mic selection to the first available input.
  useEffect(() => {
    if (!selectedMicrophoneId && microphones[0]) {
      setSelectedMicrophoneId(microphones[0].deviceId);
    }
  }, [microphones, selectedMicrophoneId]);

  // Reflect permission failures back into the toggles.
  useEffect(() => {
    if (camera.state === "denied" || camera.state === "error") {
      setCameraOn(false);
    }
  }, [camera.state]);

  useEffect(() => {
    if (microphone.state === "error") {
      setMicOn(false);
    }
  }, [microphone.state]);

  const toggleCamera = useCallback(() => {
    const next = !cameraOn;
    setCameraOn(next);
    if (next) {
      void camera.start(selectedCameraId ?? undefined);
    } else {
      camera.stop();
    }
  }, [cameraOn, camera, selectedCameraId]);

  const toggleMic = useCallback(() => {
    const next = !micOn;
    setMicOn(next);
    if (next) {
      void microphone.startRecording();
    } else {
      microphone.reset();
    }
  }, [micOn, microphone]);

  const handleSelectCamera = useCallback(
    (deviceId: string) => {
      setSelectedCameraId(deviceId);
      if (cameraOn) {
        void camera.start(deviceId);
      }
    },
    [camera, cameraOn],
  );

  const handleSelectMicrophone = useCallback((deviceId: string) => {
    // The mic device is applied when the realtime capture layer lands; for the
    // shell we only persist the selection.
    setSelectedMicrophoneId(deviceId);
  }, []);

  const handleEnd = useCallback(() => {
    camera.stop();
    microphone.reset();
    router.push(`/interviews/${interviewId}`);
  }, [camera, microphone, router, interviewId]);

  if (!hasJoined) {
    return (
      <PreJoinScreen
        header={header}
        stream={camera.stream}
        cameraState={camera.state}
        cameraError={camera.error}
        micError={microphone.error}
        cameraOn={cameraOn}
        micOn={micOn}
        onToggleCamera={toggleCamera}
        onToggleMic={toggleMic}
        cameras={cameras}
        microphones={microphones}
        selectedCameraId={selectedCameraId}
        selectedMicrophoneId={selectedMicrophoneId}
        onSelectCamera={handleSelectCamera}
        onSelectMicrophone={handleSelectMicrophone}
        onJoin={() => setHasJoined(true)}
        backHref={`/interviews/${interviewId}`}
      />
    );
  }

  return (
    <div className="flex h-screen flex-col bg-[#0a0e17] text-slate-100">
      <RoomTopBar
        header={header}
        phase={MOCK_PHASE}
        elapsedSeconds={elapsedSeconds}
        connectionStatus={connectionStatus}
      />

      <div className="relative flex flex-1 overflow-hidden">
        <main className="flex flex-1 items-center justify-center overflow-auto p-4 sm:p-6">
          <div className="grid w-full max-w-5xl gap-4 sm:grid-cols-2">
            <InterviewerTile speaking={isInterviewerSpeaking} turnState={turnState} />
            <CandidateTile
              stream={camera.stream}
              cameraOn={cameraOn}
              micOn={micOn}
              cameraState={camera.state}
            />
          </div>
        </main>

        {captionsOpen ? (
          <div className="absolute inset-y-0 right-0 z-20 w-[min(100%,22rem)] p-3 lg:static lg:z-auto lg:w-auto lg:p-4 lg:pl-0">
            <CaptionsPanel
              open={captionsOpen}
              onClose={() => setCaptionsOpen(false)}
              captionsEnabled={captionsOpen}
              captions={captions}
            />
          </div>
        ) : null}
      </div>

      <ControlBar
        micOn={micOn}
        cameraOn={cameraOn}
        captionsOn={captionsOpen}
        onToggleMic={toggleMic}
        onToggleCamera={toggleCamera}
        onToggleCaptions={() => setCaptionsOpen((prev) => !prev)}
        onEnd={handleEnd}
        cameras={cameras}
        microphones={microphones}
        selectedCameraId={selectedCameraId}
        selectedMicrophoneId={selectedMicrophoneId}
        onSelectCamera={handleSelectCamera}
        onSelectMicrophone={handleSelectMicrophone}
      />
    </div>
  );
}
