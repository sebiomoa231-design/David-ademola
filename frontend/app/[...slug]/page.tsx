import DavidApp from "../../components/david-app";

export default function Page({ params }: { params: { slug?: string[] } }) {
  const route = params.slug?.join("/") || "dashboard";
  return <DavidApp route={route} />;
}
