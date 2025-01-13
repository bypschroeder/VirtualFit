import { generateSchema } from "@/schemas";
import useImageStore from "@/store/useImageStore";
import { UploadIcon } from "lucide-react";
import { ChangeEvent } from "react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface ImageUploaderProps {
	form: UseFormReturn<z.infer<typeof generateSchema>>;
}

const ImageUploader = ({ form }: ImageUploaderProps) => {
	const { setImage } = useImageStore();

	const handleImageUpload = (event: ChangeEvent<HTMLInputElement>) => {
		const file = event.target.files?.[0];
		if (file) {
			const maxSizeInBytes = 1024 * 1024 * 5; // 5MB
			if (file.size > maxSizeInBytes) {
				alert("Image size exceeds 5MB");
				return;
			}

			const reader = new FileReader();
			reader.onload = () => {
				if (typeof reader.result === "string") {
					setImage(reader.result);
				}
			};
			form.setValue("image", file);
			reader.readAsDataURL(file);
		}
	};

	return (
		<label
			htmlFor="file-upload"
			className="inline-flex justify-center items-center gap-2 border-input bg-background hover:bg-accent disabled:opacity-50 px-4 py-2 border rounded-md focus-visible:ring-2 focus-visible:ring-ring ring-offset-background focus-visible:ring-offset-2 h-10 font-medium text-sm hover:text-accent-foreground whitespace-nowrap transition-colors cursor-pointer disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg]:size-4 focus-visible:outline-none"
		>
			<UploadIcon />
			<span>Upload Image</span>
			<input
				type="file"
				accept="image/png, image/jpeg"
				className="sr-only"
				id="file-upload"
				onChange={handleImageUpload}
			/>
		</label>
	);
};

export default ImageUploader;
