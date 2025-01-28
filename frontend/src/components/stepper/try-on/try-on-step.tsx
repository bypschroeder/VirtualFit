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
import { Form, FormControl, FormField, FormItem } from "@/components/ui/form";
import { tryonSchema } from "@/schemas";
import useFitObjStore from "@/store/useFitObjStore";
import useFormStore from "@/store/useFormStore";
import useObjStore from "@/store/useObjStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

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
	const [loadingPreviews, setLoadingPreviews] = useState(true);
	const [loadingFit, setLoadingFit] = useState(false);
	const [previewFiles, setPreviewFiles] = useState<PreviewFile[]>([]);

	const { gender } = useFormStore();
	const { obj } = useObjStore();
	const { setFitObj, setIsFitObjLoading } = useFitObjStore();

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
				setLoadingPreviews(false);
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

	const form = useForm<z.infer<typeof tryonSchema>>({
		resolver: zodResolver(tryonSchema),
		defaultValues: {
			obj: undefined,
			garment: undefined,
			gender: gender,
			size: "M",
		},
	});

	useEffect(() => {
		if (obj) {
			const objBlob = new Blob([obj], { type: "application/octet-stream" });
			const objFile = new File([objBlob], "model.obj", {
				type: "application/octet-stream",
			});

			form.setValue("obj", objFile);
		}
	}, [obj, form]);

	const onSubmit = async (values: z.infer<typeof tryonSchema>) => {
		setFitObj(null);
		try {
			const formData = new FormData();
			formData.append("obj", values.obj);
			formData.append("garment", values.garment);
			formData.append("gender", values.gender);
			formData.append("size", values.size);

			setLoadingFit(true);
			setIsFitObjLoading(true);

			const response = await fetch("http://api.localhost/try-on", {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				throw new Error(`Error: ${response.status} - ${response.statusText}`);
			}

			const fitObj = await response.text();

			setFitObj(fitObj);
			setLoadingFit(false);
			setIsFitObjLoading(false);
		} catch (error) {
			console.error("Error generating the virutal fit", error);
			setLoadingFit(false);
			setIsFitObjLoading(false);
		}
	};

	if (loadingPreviews) {
		return (
			<Card className="flex justify-center items-center h-full">
				<CardContent>
					<LoadingSpinner />
				</CardContent>
			</Card>
		);
	}

	return (
		<Form {...form}>
			<form
				onSubmit={form.handleSubmit(onSubmit)}
				className="flex flex-col gap-4 h-full"
			>
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
										{category.type.charAt(0).toUpperCase() +
											category.type.slice(1)}
									</AccordionTrigger>
									{/* TODO: ScrollArea instead of overflow-y-scroll */}
									<AccordionContent>
										<FormField
											control={form.control}
											name="garment"
											render={({ field }) => (
												<FormItem>
													<FormControl>
														<div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 max-h-[20rem] overflow-y-scroll">
															{category.items.map((item) => (
																<Card
																	key={item.name}
																	className={`w-full h-full cursor-pointer ${
																		field.value === item.name
																			? "bg-primary/10 border-primary"
																			: ""
																	} ${
																		loadingFit
																			? "opacity-50 cursor-not-allowed"
																			: ""
																	}`}
																	onClick={() => {
																		if (!loadingFit) {
																			field.onChange(item.name);
																		}
																	}}
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
														</div>
													</FormControl>
												</FormItem>
											)}
										/>
									</AccordionContent>
								</AccordionItem>
							))}
						</Accordion>
					</CardContent>
					<CardFooter className="flex flex-col justify-center items-center gap-6">
						<SizePicker form={form} disabled={loadingFit} />
						<Button size={"lg"} disabled={loadingFit}>
							{loadingFit ? <LoadingSpinner /> : "Try on"}
						</Button>
					</CardFooter>
				</Card>
			</form>
		</Form>
	);
};

export default TryOnStep;
