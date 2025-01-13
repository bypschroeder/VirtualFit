import LoadingSpinner from "@/components/loading-spinner";
import SizePicker from "@/components/stepper/try-on/size-picker";
import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import useFormStore from "@/store/useFormStore";
import { useEffect, useState } from "react";

type ClothingType = "t-shirt" | "sweatshirt" | "hoodie" | "pants";

const clothingTypeMap: Record<ClothingType, "tops" | "bottoms"> = {
	"t-shirt": "tops",
	sweatshirt: "tops",
	hoodie: "tops",
	pants: "bottoms",
};

interface PreviewFile {
	name: string;
	path: string;
}

const TryOnStep = () => {
	const [selectedItem, setSelectedItem] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);
	const [previewFiles, setPreviewFiles] = useState<PreviewFile[]>([]);

	const { gender } = useFormStore();

	const handleSelectItem = (itemName: string) => {
		setSelectedItem(itemName);
	};

	useEffect(() => {
		const fetchPreviews = async () => {
			try {
				const formData = new FormData();
				if (gender) {
					formData.append("gender", gender);
				} else {
					console.error("Gender is undefined");
					return;
				}

				const response = await fetch("http://api.localhost/generate-previews", {
					method: "POST",
					body: formData,
				});

				if (!response.ok) {
					throw new Error(`Error: ${response.status} - ${response.statusText}`);
				}

				const data = await response.json();
				const presignedUrls = data.presigned_urls;

				const downloadedFiles = [];

				for (const index in presignedUrls) {
					const url = presignedUrls[index];
					const fileResponse = await fetch(url, {
						method: "GET",
					});

					if (!fileResponse.ok) {
						throw new Error(
							`Error: ${fileResponse.status} - ${fileResponse.statusText}`
						);
					}

					const blob = await fileResponse.blob();
					const objectUrl = URL.createObjectURL(blob);
					const parts = url.split("/");
					downloadedFiles.push({
						name: parts[parts.length - 2],
						path: objectUrl,
					});
				}
				setPreviewFiles(downloadedFiles);
				setLoading(false);
			} catch (error) {
				console.error("Error fetching previews: ", error);
			}
		};
		fetchPreviews();
	}, [gender]);

	const categories = [
		{
			type: "tops",
			items: previewFiles.filter(
				(file) => clothingTypeMap[file.name as ClothingType] === "tops"
			),
		},
		{
			type: "bottoms",
			items: previewFiles.filter(
				(file) => clothingTypeMap[file.name as ClothingType] === "bottoms"
			),
		},
	];

	if (loading) {
		return (
			<Card className="flex justify-center items-center h-full">
				<CardContent>
					<LoadingSpinner />
				</CardContent>
			</Card>
		);
	}

	return (
		<Card className="flex flex-col justify-center items-center h-full">
			<CardContent className="py-4 w-full h-full">
				<Accordion
					type="single"
					defaultValue={categories[0].type}
					collapsible
					className="flex flex-col items-center gap-4 w-full h-full jusify-center"
				>
					{categories.map((category) => (
						<AccordionItem
							className="w-full"
							key={category.type}
							value={category.type}
						>
							<AccordionTrigger className="w-full">
								{category.type.charAt(0).toUpperCase() + category.type.slice(1)}
							</AccordionTrigger>
							{/* TODO: ScrollArea instead of overflow-y-scroll */}
							<AccordionContent className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 max-h-[20rem] overflow-y-scroll">
								{category.items.map((item) => (
									<Card
										key={item.name}
										className={`w-full h-full cursor-pointer ${
											selectedItem === item.name
												? "bg-primary/10 border-primary"
												: ""
										}`}
										onClick={() => handleSelectItem(item.name)}
									>
										<CardContent className="p-2">
											<img
												src={item.path}
												alt={item.name}
												className="w-full h-full object-cover"
											/>
										</CardContent>
									</Card>
								))}
							</AccordionContent>
						</AccordionItem>
					))}
				</Accordion>
			</CardContent>
			<CardFooter className="flex flex-col justify-center items-center gap-6">
				<SizePicker />
				<Button size={"lg"}>Try on</Button>
			</CardFooter>
		</Card>
	);
};

export default TryOnStep;
