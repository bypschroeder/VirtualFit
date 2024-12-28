import { useCamera } from "@/components/ui/camera/camera-provider"; // Adjust import path as necessary
import { TriangleAlert, X } from "lucide-react";
import React, { useEffect, useImperativeHandle, useState } from "react";
import { CameraProps, defaultErrorMessages } from "./camera-types";

export const CameraView = React.forwardRef<unknown, CameraProps>(
	(
		{ errorMessages = defaultErrorMessages, videoReadyCallback = () => null },
		ref
	) => {
		const {
			playerRef,
			canvasRef,
			containerRef,
			notSupported,
			permissionDenied,
			activeDeviceId,
			initCameraStream,
			takePhoto,
			stopStream,
		} = useCamera();

		useImperativeHandle(ref, () => ({
			takePhoto,
			stopCamera: stopStream,
		}));

		useEffect(() => {
			async function init() {
				await initCameraStream();
			}
			init();
		}, [activeDeviceId]);

		return (
			<div
				ref={containerRef}
				className="bg-muted min-h-[calc(100vh_-_theme(spacing.16))]"
			>
				<div className="top-0 left-0 absolute w-full h-svh">
					<WarningMessage
						message={errorMessages.noCameraAccessible!}
						show={notSupported}
					/>
					<WarningMessage
						message={errorMessages.permissionDenied!}
						show={permissionDenied}
					/>
					<video
						className={"z-0 h-svh w-full transform object-cover"}
						ref={playerRef}
						id="video"
						muted={true}
						autoPlay={true}
						playsInline={true}
						onLoadedData={videoReadyCallback}
					></video>
					<canvas className="hidden" ref={canvasRef} />
				</div>
			</div>
		);
	}
);

CameraView.displayName = "CameraView";

function WarningMessage({ message, show }: { message: string; show: boolean }) {
	const [toShow, setShow] = useState(show);
	return toShow ? (
		<div className="bg-yellow-50 p-4 rounded-md">
			<div className="flex">
				<div className="flex-shrink-0">
					<TriangleAlert
						className="w-5 h-5 text-yellow-400"
						aria-hidden="true"
					/>
				</div>
				<div className="ml-3">
					<h3 className="font-medium text-sm text-yellow-800">
						Attention needed
					</h3>
					<div className="mt-2 text-sm text-yellow-700">
						<p>{message}</p>
					</div>
				</div>
				<div className="ml-auto pl-3">
					<div className="-mx-1.5 -my-1.5">
						<button
							type="button"
							className="inline-flex bg-yellow-50 hover:bg-yellow-100 p-1.5 rounded-md focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50 text-yellow-500 focus:outline-none"
							onClick={() => setShow(false)}
						>
							<span className="sr-only">Dismiss</span>
							<X className="w-5 h-5" aria-hidden="true" />
						</button>
					</div>
				</div>
			</div>
		</div>
	) : null;
}
