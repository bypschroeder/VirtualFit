import { Button } from "@/components/ui/button";
import { useCamera } from "@/components/ui/camera/camera-provider";
import { CameraType } from "@/components/ui/camera/camera-types";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { ArrowLeftRight, Check, GalleryVerticalEnd, X } from "lucide-react";
import { FC, useRef } from "react";
import { CameraView } from "./camera-view";

interface CameraProps {
	onClosed: () => void;
	onCapturedImages: (images: string[]) => void;
}

const Camera: FC<CameraProps> = ({ onClosed, onCapturedImages }) => {
	const camera = useRef<CameraType>();
	const { images, addImage, numberOfCameras, resetImages, stopStream } =
		useCamera();

	const handleCapture = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault();
		if (camera.current) {
			const imageData = camera.current.takePhoto();
			if (imageData) {
				addImage(imageData);
			}
		}
	};

	const handleOnClosed = () => {
		stopStream();
		onClosed();
	};
	const handleOnCapturedImages = (images: string[]) => {
		onCapturedImages(images);
		resetImages();
		handleOnClosed();
	};
	return (
		<div className="z-10 flex flex-col flex-1 min-w-[calc(100vw_-_theme(spacing.4))]">
			<div className="relative w-full">
				<div className="z-10 absolute w-full md:w-[20%] md:h-[calc(93vh_-_theme(spacing.12))]">
					<div className="relative top-0 left-2">
						<Button
							className="opacity-40 hover:opacity-100 p-4 rounded-full"
							size={"icon"}
							variant={images.length > 0 ? "destructive" : "default"}
							onClick={handleOnClosed}
						>
							<X className="fixed w-6 h-6" />
						</Button>
					</div>
					{images.length > 0 && (
						<div className="top-0 md:top-auto right-6 md:right-0 md:bottom-0 md:left-2 z-10 absolute">
							<Button
								className="opacity-40 hover:opacity-100 p-4 rounded-full"
								size={"icon"}
								variant={"secondary"}
								onClick={() => {
									handleOnCapturedImages(images);
								}}
							>
								<Check className="fixed w-6 h-6" />
							</Button>
						</div>
					)}
				</div>

				<CameraView ref={camera} />
				<div className="md:top-[50%] md:right-14 bottom-0 md:bottom-auto left-[45%] md:left-auto z-20 absolute">
					<Button
						className={cn(
							"group h-12 w-12  rounded-full p-8 opacity-40 hover:opacity-100  "
						)}
						size={"icon"}
						variant={"default"}
						onClick={(e) => {
							handleCapture(e);
						}}
					>
						<div className="group-hover:bg-primary-foreground/60 fixed bg-primary-foreground rounded-full w-11 h-11"></div>
					</Button>
				</div>

				<div
					className={cn(
						"absolute z-10 w-full md:right-0 md:top-0  md:h-[calc(93vh_-_theme(spacing.12))] md:w-[20%]"
					)}
				>
					{images.length > 0 && (
						<div className="md:top-0 md:right-14 bottom-0 md:bottom-auto left-2 md:left-auto absolute">
							<Gallery />
						</div>
					)}

					{numberOfCameras > 0 && (
						<div className="md:top-auto right-6 md:right-14 bottom-0 md:bottom-0 z-10 absolute">
							<SwitchCamera />
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

function SwitchCamera() {
	const { devices, setActiveDeviceId, activeDeviceId, switchCamera } =
		useCamera();

	if (devices.length === 2) {
		return (
			<Button
				variant="default"
				size="icon"
				className="opacity-40 hover:opacity-100 p-4 rounded-full"
				onClick={switchCamera}
			>
				<ArrowLeftRight className="fixed w-6 h-6" />
			</Button>
		);
	}
	return (
		<Dialog>
			<DialogTrigger asChild>
				<Button
					variant={"default"}
					size={"icon"}
					className="opacity-40 hover:opacity-100 p-4 rounded-full"
				>
					<ArrowLeftRight className="fixed w-6 h-6" />
				</Button>
			</DialogTrigger>
			<DialogContent className="sm:max-w-[425px]">
				<DialogHeader>
					<DialogTitle>Switch Camera</DialogTitle>
				</DialogHeader>
				<DialogDescription>
					<Select
						onValueChange={(value) => {
							setActiveDeviceId(value);
						}}
					>
						<SelectTrigger>
							<SelectValue placeholder="Choose Camera" />
						</SelectTrigger>
						<SelectContent>
							{devices.map((device) => (
								<SelectItem key={device.deviceId} value={device.deviceId}>
									{device.label}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</DialogDescription>
			</DialogContent>
		</Dialog>
	);
}

function Gallery() {
	const { images, removeImage } = useCamera();
	return (
		<Dialog>
			<DialogTrigger asChild>
				<Button
					className="opacity-40 hover:opacity-100 p-4 rounded-full"
					size={"icon"}
					variant={"default"}
				>
					<GalleryVerticalEnd className="fixed w-6 h-6" />
				</Button>
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>{images.length} Photos</DialogTitle>
				</DialogHeader>
				<ScrollArea className="h-[calc(80vh-_theme(spacing.16))]">
					<div className="gap-2 grid grid-cols-2">
						{images.map((image, index) => (
							<div key={index} className="relative">
								<img src={image} alt="captured" />
								<Button
									className="top-2 right-2 absolute opacity-40 hover:opacity-100 p-2 rounded-full w-6 h-6"
									size={"icon"}
									variant={"destructive"}
									onClick={() => {
										removeImage(index);
									}}
								>
									<X className="fixed w-4 h-4" />
								</Button>
							</div>
						))}
					</div>
				</ScrollArea>
			</DialogContent>
		</Dialog>
	);
}

export default Camera;
