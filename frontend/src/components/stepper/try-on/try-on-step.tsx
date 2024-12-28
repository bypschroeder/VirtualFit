import SizePicker from "@/components/stepper/try-on/size-picker";
import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { useState } from "react";

const mock_clothes = [
	{
		type: "tops",
		items: [
			{
				name: "T-Shirt",
				path: "/t-shirt.png",
			},
			{
				name: "Sweatshirt",
				path: "/t-shirt.png",
			},
			{
				name: "Hoodie",
				path: "/t-shirt.png",
			},
			{
				name: "Shirt",
				path: "/t-shirt.png",
			},
			{
				name: "Polo",
				path: "/t-shirt.png",
			},
			{
				name: "Turtleneck",
				path: "/t-shirt.png",
			},
			{
				name: "Blouse",
				path: "/t-shirt.png",
			},
			{
				name: "Oversized T-Shirt",
				path: "/t-shirt.png",
			},
		],
	},
	{
		type: "bottoms",
		items: [
			{
				name: "Pants",
				path: "/t-shirt.png",
			},
			{
				name: "Shorts",
				path: "/t-shirt.png",
			},
		],
	},
];

const TryOnStep = () => {
	const [selectedItem, setSelectedItem] = useState<string | null>(null);

	const handleSelectItem = (itemName: string) => {
		setSelectedItem(itemName);
	};

	return (
		<Card className="flex flex-col justify-center items-center h-full">
			<CardContent className="py-4 w-full h-full">
				<Accordion
					type="single"
					defaultValue={mock_clothes[0].type}
					collapsible
					className="flex flex-col items-center gap-4 w-full h-full jusify-center"
				>
					{mock_clothes.map((category) => (
						<AccordionItem
							className="w-full"
							key={category.type}
							value={category.type}
						>
							<AccordionTrigger className="w-full">
								{category.type.charAt(0).toUpperCase() + category.type.slice(1)}
							</AccordionTrigger>
							{/* TODO: ScrollArea instead of overflow-y-scroll */}
							<AccordionContent className="gap-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 max-h-[20rem] overflow-y-scroll">
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
