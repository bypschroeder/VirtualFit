import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import { FormControl, FormField, FormItem } from "@/components/ui/form";
import { tryonSchema } from "@/schemas";
import useFitObjStore from "@/store/useFitObjStore";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface PreviewFile {
	name: string;
	path: string;
}

interface ClothingPickerProps {
	form: UseFormReturn<z.infer<typeof tryonSchema>>;
	categories: { type: string; items: PreviewFile[] }[];
}

const ClothingPicker = ({ form, categories }: ClothingPickerProps) => {
	const { isFitObjLoading } = useFitObjStore();
	return (
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
														isFitObjLoading
															? "opacity-50 cursor-not-allowed"
															: ""
													}`}
													onClick={() => {
														if (!isFitObjLoading) {
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
	);
};

export default ClothingPicker;
