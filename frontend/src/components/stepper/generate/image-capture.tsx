import LoadingSpinner from "@/components/loading-spinner";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import {
	HoverCard,
	HoverCardContent,
	HoverCardTrigger,
} from "@/components/ui/hover-card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import useImageStore from "@/store/useImageStore";
import { CameraIcon, Info, Timer } from "lucide-react";
import { useRef, useState } from "react";
import Webcam from "react-webcam";

interface ImageCaptureProps {
	form: any; // TODO: Fix form type
}

const ImageCapture = ({ form }: ImageCaptureProps) => {
	const webcamRef = useRef<Webcam>(null);
	const [showDialog, setShowDialog] = useState<boolean>(false);
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [timer, setTimer] = useState<number>(0);
	const [countdown, setCountdown] = useState<number>(0);

	const { setImage } = useImageStore();

	const handleUserMedia = () => {
		setIsLoading(false);
	};

	const startCountdownAndCapture = () => {
		if (timer > 0) {
			let currentCountdown = timer;
			setCountdown(currentCountdown);

			const countdownInterval = setInterval(() => {
				console.log(currentCountdown);
				currentCountdown--;
				setCountdown(currentCountdown);

				if (currentCountdown === 0) {
					clearInterval(countdownInterval);
					captureScreenshot();
				}
			}, 1000);
		} else {
			captureScreenshot();
		}
	};

	const captureScreenshot = () => {
		if (webcamRef.current) {
			const screenshot = webcamRef.current.getScreenshot();
			if (screenshot) {
				const byteString = atob(screenshot.split(",")[1]);
				const arrayBuffer = new ArrayBuffer(byteString.length);
				const uint8Array = new Uint8Array(arrayBuffer);

				for (let i = 0; i < byteString.length; i++) {
					uint8Array[i] = byteString.charCodeAt(i);
				}

				const blob = new Blob([uint8Array], { type: "image/png" });

				const file = new File([blob], "screenshot.png", { type: "image/png" });

				setImage(URL.createObjectURL(file));
				form.setValue("image", file);
				setCountdown(0);
				setShowDialog(false);
			}
		}
	};
	return (
		<Dialog
			open={showDialog}
			onOpenChange={(open) => {
				setShowDialog(open);
				if (open) setIsLoading(true);
			}}
		>
			<DialogTrigger asChild>
				<Button variant={"outline"}>
					<CameraIcon size={20} />
					<span>Capture Photo</span>
					<span className="sr-only">Capture</span>
				</Button>
			</DialogTrigger>
			<DialogContent className="p-0 border-none max-w-7xl">
				<DialogTitle className="hidden" />
				{isLoading && (
					<div className="absolute inset-0 flex justify-center items-center">
						<LoadingSpinner />
					</div>
				)}
				<Webcam
					ref={webcamRef}
					audio={false}
					screenshotFormat="image/png"
					className="rounded-md w-full h-full object-scale-down"
					videoConstraints={{
						width: 1280,
						height: 720,
						aspectRatio: 16 / 9,
					}}
					onUserMedia={() => handleUserMedia()}
				/>
				{countdown !== 0 && (
					<span className="bottom-1/2 left-1/2 absolute drop-shadow-[0_1.2px_1.2px_rgba(0,0,0,0.8)] font-bold text-7xl text-white translate-y-1/2">
						{countdown}
					</span>
				)}
				<div className="right-4 bottom-4 absolute flex items-center gap-4">
					<HoverCard>
						<HoverCardTrigger>
							<Info className="drop-shadow-[0_1.2px_1.2px_rgba(0,0,0,0.8)] w-8 h-8 text-primary-foreground hover:text-primary-foreground/60" />
						</HoverCardTrigger>
						<HoverCardContent>
							<p className="font-bold">
								Please ensure your entire body is visible in the photo.
							</p>
							<p>
								For accurate generation, the image must include your full body
								from head to toe without any obstructions.
							</p>
						</HoverCardContent>
					</HoverCard>
					<Select
						value={String(timer)}
						onValueChange={(value) => setTimer(Number(value))}
					>
						<SelectTrigger className="flex justify-center items-center gap-2">
							<Timer className="w-6 h-6 text-muted-foreground" />
							<SelectValue>
								<span className="font-semibold text-lg">{timer}</span>
							</SelectValue>
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="0">0</SelectItem>
							<SelectItem value="3">3</SelectItem>
							<SelectItem value="5">5</SelectItem>
							<SelectItem value="7">7</SelectItem>
							<SelectItem value="10">10</SelectItem>
						</SelectContent>
					</Select>
					<Button
						onClick={() => startCountdownAndCapture()}
						disabled={isLoading || countdown > 0}
					>
						<CameraIcon size={20} />
						<span>Capture Photo</span>
						<span className="sr-only">Capture</span>
					</Button>
				</div>
			</DialogContent>
		</Dialog>
	);
};

export default ImageCapture;
