#!/usr/bin/perl
use strict;

binmode STDOUT, ":utf8";

sub get_data_list {
	my $xpath = $_[0];
	my $query = $_[1];
	my $node = $_[2];
	my @nodes = $xpath->findnodes($query, $node);
	my @values;
	foreach (@nodes) {
		my $str = $_->getData();
		$str =~ s/[\n\r\t]+/ /g;
		if ($str) {
			push(@values, $str);
		}
	}
	return @values;
}

sub get_data_item {
	my @values = get_data_list($_[0], $_[1], $_[2]);
	return @values[0];
}

unless (@ARGV == 1) {
	print STDERR "<xml file>\n";
	exit 1;
}

use XML::XPath;

my $xpath = XML::XPath->new(filename => $ARGV[0]);
my $nodes = $xpath->find('/eeml/environment');

unless ($nodes->isa('XML::XPath::NodeSet')) {
	print STDERR "Query didn't return a nodeset. Value: ";
	print $nodes->value, "\n";
	exit 1;
}
if ($nodes->size) {
	print STDERR "Found ", $nodes->size, " environments.\n";
	foreach my $node ($nodes->get_nodelist) {
		my $id = get_data_item($xpath, '@id', $node);
		my $created_at = get_data_item($xpath, '@created', $node);
		my $updated_at = get_data_item($xpath, '@updated', $node);
		my $title = get_data_item($xpath, 'title/text()', $node);
		my $feed = get_data_item($xpath, 'feed/text()', $node);
		my $status = get_data_item($xpath, 'status/text()', $node);
		my $private = get_data_item($xpath, 'private/text()', $node);
		my $location_name = get_data_item($xpath, 'location/name/text()', $node);
		my $location_lat = get_data_item($xpath, 'location/lat/text()', $node);
		my $location_lon = get_data_item($xpath, 'location/lon/text()', $node);
		
		my @env_tags = get_data_list($xpath, 'tag/text()', $node);
		# print join(", ", sort(@env_tags)), "\n";
		
		my @streams = $xpath->findnodes('data', $node);
		foreach (@streams) {
			my $stream_id = get_data_item($xpath, '@id', $_);
			my $stream_unit = get_data_item($xpath, 'unit/text()', $_);
			my $stream_value = get_data_item($xpath, 'current_value/text()', $_);
			my $stream_last_sample_time = get_data_item($xpath, 'current_value/@at', $_);
			my @stream_tags = get_data_list($xpath, 'tag/text()', $_);
			
			# ID	CREATED_AT	TITLE	FEED	STATUS	PRIVATE	LOCATION	LAT	LON	ENV_TAGS	STREAM_ID	STREAM_UNIT	STREAM_TIMESTAMP	STREAM_TAGS

			# First: env metadata, repeated once per stream
			my $jtags = join(", ", sort(@env_tags));
			print "${id}\t${created_at}\t${updated_at}\t${title}\t${feed}\t${status}\t${private}\t${location_name}\t${location_lat}\t${location_lon}\t${jtags}\t";
			
			# Followed up by stream data and metadata
			$jtags = join(", ", sort(@stream_tags));
			print "${stream_id}\t${stream_unit}\t${stream_value}\t${stream_last_sample_time}\t${jtags}\t";
			
			# Followed up by unified tag list
			my @tags = @env_tags;
			push(@tags, @stream_tags);
			my %tags_hash = map { $_, 1 } @tags;
			@tags = sort(keys %tags_hash);
			$jtags = join(", ", @tags);
			print "${jtags}\n";
		}
	}
}
else {
	print STDERR "No nodes found";
}
