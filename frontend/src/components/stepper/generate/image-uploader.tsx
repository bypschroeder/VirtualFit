import { handleImageUpload } from "@/lib/handlers";
import { generateSchema } from "@/schemas";
import useImageStore from "@/store/useImageStore";
import { UploadIcon } from "lucide-react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface ImageUploaderProps {
	form: UseFormReturn<z.infer<typeof generateSchema>>;
}

const ImageUploader = ({ form }: ImageUploaderProps) => {
	// State Management
	const { setImage } = useImageStore();

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
				onChange={(event) => handleImageUpload(event, setImage, form)}
			/>
		</label>
	);
};

export default ImageUploader;
